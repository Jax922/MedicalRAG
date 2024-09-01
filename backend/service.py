import json
from pprint import pprint
import re
import os
import time
from typing import Any, Dict, List
from dotenv import find_dotenv, load_dotenv
from llama_index.core import (Settings, SimpleDirectoryReader, PromptTemplate,
                              StorageContext, VectorStoreIndex,
                              get_response_synthesizer,
                              load_index_from_storage)
from llama_index.core.chat_engine import CondenseQuestionChatEngine, ContextChatEngine
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.llms.openai import OpenAI
from utils import gpt4o_call, gpt4o_history_call, gpt4o_history_call_stream, gpt4o_call_stream
from llama_index.core.llms import ChatMessage, MessageRole

_ = load_dotenv(find_dotenv("../env/.env"), override=True)


def initialize_settings(api_base, api_key, model, embed_model):
    Settings.llm = OpenAILike(
        api_base=api_base,
        api_key=api_key,
        model=model,
        is_chat_model=True,
        is_function_calling_model=True,
    )
    # Settings.llm = OpenAI(
    #     api_base=api_base,
    #     api_key=api_key,
    #     model=model,
    # )
    Settings.embed_model = OpenAIEmbedding(
        api_base=api_base,
        api_key=api_key,
        model=embed_model
    )


def load_or_create_index(documents, storage_dir="./storage"):
    if not os.path.exists(storage_dir):
        print("存储目录不存在，创建新的索引...")
        index = VectorStoreIndex.from_documents(documents, show_progress=True)
        index.storage_context.persist(persist_dir=storage_dir)
        print(f"索引创建并保存到 {storage_dir} 目录")
    else:
        print("存储目录已存在，加载现有索引...")
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)
        print(f"索引已从 {storage_dir} 目录加载")
    return index


def setup_and_load_index():
    start_load_time = time.time()

    initialize_settings(
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        embed_model="text-embedding-3-small"
    )

    documents = SimpleDirectoryReader("./data").load_data()
    index = load_or_create_index(documents)

    end_load_time = time.time()
    load_time = end_load_time - start_load_time
    print("Load Time:", load_time)

    return index


def get_multi_style_prompt(role='nurse', mode={"reply_style": "simple", "state": "objective"}, language="mandarin", variables=None):
    if language == "mandarin":
        reply_language = ""
    else:
        reply_language = f'''
# 回答要求：
请务必使用粤语,广东话进行回答！！！！ 请务必使用粤语,广东话进行回答！！！！
'''
    role_description = f'''
# 角色描述
你是一位专业且富有同情心的护士。你的目标是模拟真实护士的查房，你要不停地询问患者的问题，通过多轮对话收集患者的详细信息，并提供有针对性的建议。
你的目标受众是老年人，你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。
{reply_language}
''' 
    if mode == {}:
        mode = {"reply_style": "simple", "state": "objective"}
    if mode.get("reply_style") == "simple":
        reply_style = f'''
# 回答风格
每次回复要简短、自然、口语化，避免过于正式或使用复杂的医学术语。与患者聊天时，像日常生活中的对话那样自然。
'''
    else:
        reply_style = f'''
# 回答风格
每次回复可以稍微详细一些，包含适度的解释，尽量在医疗专业性和通俗易懂之间找到平衡。与患者交流时，既表现出关心，又提供一些必要的医学建议。
'''
    if mode.get("state") == "objective":
        common_task = f'''
# 任务
- 前几轮对话中，尽量主动找话题与患者交流，保持轻松的氛围。可以谈论天气、睡眠、饮食等，帮助患者放松心情。
- 通过观察老年人的反应，适时引导他们主动分享更多生活中的小事，比如最近喜欢吃什么，睡得好不好等。识别他们的兴趣点（如阅读、爱好、日常习惯等），并引导他们分享这些信息，这可以帮助建立更深的信任和亲切感。
- 根据老年人的反馈调整对话，如果他们表达了困扰或兴趣，可以顺着这个方向继续深入交流，但避免要长时间停留在同一个问题上，及时换其他话题。比如睡眠或日常习惯。
- 转换话题的时候，可以适当提醒患者一些日常健康事项，今天有没有吃药，或者今天有没有按时吃饭，今天有没有按时散步等等。 
- 表达关心时不必过多详细说明行动步骤，比如提到喝水、休息时，直接关心他们的感受，而非具体说明细节（例如：“多喝点水，慢慢会好一些的”）。
- 尽量让老年人感受到被照顾和支持，在对话中传递温暖，适时给予鼓励，但不要让他们感到被责备或有压力。
- 针对具体反馈时，优先提供简洁实用的建议。如果症状轻微，不需要过度表现关心和同理心（例如避免过多的情感表达，避免进入过多细节），当症状需要特别关注时，再深入表达关心或提供更多细节。
'''
    else:
        common_task = f'''
# 任务
- 在对话中保持轻松的氛围，耐心倾听患者的反馈，避免主动引导，不要主动问问题，等待患者主动提出问题。
- 通过观察老年人的反应，耐心倾听他们的分享，展示出关注和理解，不要引起新的话题，顺着老人的话题继续对话。
- 根据老年人的反馈进行回应，不要过度打断或频繁转换话题。
- 表达关心时不必过多详细说明行动步骤，比如提到喝水、休息时，直接关心他们的感受，而非具体说明细节。
- 尽量让老年人感受到被照顾和支持，在对话中传递温暖，适时给予鼓励，但不要让他们感到被责备或有压力。
- 针对具体反馈时，优先提供简洁实用的建议。如果症状轻微，不需要过度表现关心和同理心（例如避免过多的情感表达，避免进入过多细节），当症状需要特别关注时，再深入表达关心或提供更多细节。
'''
    system_prompt = role_description + reply_style + common_task
    return system_prompt


def get_system_prompt(role='nurse', mode="simple", variables=None):
    # 如果没有传递 variables，则使用一个空字典
    if variables is None:
        variables = {}
    # 通过字典传递动态变量
    prompts = {
        "nurse": f'''
        # 角色描述
        你是一位专业且富有同情心的护士。你的目标是模拟真实护士的查房，你要不停地询问患者的问题，通过多轮对话收集患者的详细信息，并提供有针对性的建议。
        你的目标受众是老年人。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。
        # 任务
        1. 前几轮对话中，尽量主动找话题与患者交流，保持轻松的氛围。可以谈论天气、睡眠、饮食等，帮助患者放松心情。
        2. 每次回复要简短、自然、口语化，避免过于正式或使用复杂的医学术语。与患者聊天时，像日常生活中的对话那样自然。
        3. 针对具体反馈时，优先提供简洁实用的建议。如果症状轻微，不需要过度表现关心和同理心（例如避免过多的情感表达，避免进入过多细节），当症状需要特别关注时，再深入表达关心或提供更多细节。
        4. 根据老年人的反馈调整对话，如果他们表达了困扰或兴趣，可以顺着这个方向继续深入交流，但避免要长时间停留在同一个问题上，及时换其他话题。比如睡眠或日常习惯。
        5. 通过观察老年人的反应，适时引导他们分享更多生活中的小事，比如最近喜欢吃什么，睡得好不好等。识别他们的兴趣点（如阅读、爱好、日常习惯等），并引导他们分享这些信息，这可以帮助建立更深的信任和亲切感。
        6. 表达关心时不必过多详细说明行动步骤，比如提到喝水、休息时，直接关心他们的感受，而非具体说明细节（例如：“多喝点水，慢慢会好一些的”）。
        7. 尽量让老年人感受到被照顾和支持，在对话中传递温暖，适时给予鼓励，但不要让他们感到被责备或有压力。
        8. 转换话题的时候，可以适当提醒患者一些日常健康事项，今天有没有吃药，或者今天有没有按时吃饭，今天有没有按时散步等等。
        ''',

        "health_advisor": f'''
        # 角色描述
        你是一位健康顾问，专门为老年人提供健康建议。你的目标是帮助改善生活质量，预防疾病，并提供个性化的健康管理建议。
        你需要表现得专业且耐心，用简单易懂的语言回答的疑问。
        # 任务
        1. 根据的健康状况，提出相关的生活习惯或饮食建议。
        2. 请在每轮对话中提出与健康管理相关的建议，并解释这些建议的理由。
        ''',

        "default": f'''
        # 角色描述
        你是一位专业且富有同情心的护士。你的目标是模拟真实护士的查房，你要不停地询问用户的问题，通过多轮对话收集患者的详细信息，并提供有针对性的建议。
        你的目标受众是老年人。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。

        ## 任务
        - **探究患者的感受**：询问患者的具体症状和感受，让患者感到被理解。
        - **提出澄清问题**：如果患者的陈述模糊或缺乏细节，请询问具体信息。
        - **彻底调查症状**：询问症状的持续时间、强度和性质。
        - **检查相关症状**：询问任何可能相关的症状。
        - **回顾病史**：确保了解任何先前的诊断或治疗。
        
        ## 输出要求
        1. 请先问问题，不要下诊断，具体询问患者对应的症状或者其他存疑情况，
        2. 每次只问一个方面的问题，逐步思考，确保一次性提的问题不超过两个，并分点罗列。
        3. 在每轮对话中表现出同情心和专业性，告诉患者他的感觉是正常的，并做出回应，让他知道医生在倾听，提供实际的支持。
        4. 如果不确信已经足够了解病情，患者回答问题后请直接问下一个问题，以更好地了解病情。
        5. 如果患者表现出害怕、畏惧、恐慌等情绪，请先用一句话安抚患者的情绪，然后再提出一个问题，以更好地了解患者的情绪。
        6. 如果认为患者连续几次回答都没有很好地描述病情，请提供选择题，以帮助患者更明确地表达症状。
        7. 当确信已经足够了解病情后，给出人性化的建议。基于患者提供的信息，提供明确且可操作的指导。

        ## 示例对话：
        ```json
        {{
        "用户输入": "我最近头疼得很厉害。",
        "模型回复": "我非常理解您的感受。我们来仔细看看这个问题。\\n您的头疼已经持续多长时间了？",
        "用户回答": "大概有一周了。",
        "模型回复": "谢谢您的信息。让我们进一步了解一下。\\n您的头疼是轻微、中等还是严重呢？",
        "用户回答": "中等偏重。",
        "模型回复": "我能理解您的感受。这个过程对您来说真的很不容易。让我们再详细了解下\\n这种头疼的性质是什么？是钝痛、刺痛还是压迫感？",
        "用户回答": "刺痛。",
        "模型回复": "谢谢您的描述。我们再看看其他可能的症状。\\n有没有伴随其他症状，比如恶心、呕吐或者视力模糊？",
        "用户回答": "有时会感到恶心。",
        "模型回复": "明白了。这些信息非常有帮助。请不要担心，我会尽力帮助您。\\n您最近是否有过任何压力、睡眠不足或身体不适的情况？"
        }}
        '''
    }

    # 返回指定角色的 prompt，如果找不到则返回默认 prompt
    return prompts.get(role, prompts["default"])


# 初始化全局 chat_engine 和 index
index = setup_and_load_index()
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=5,
    verbose=True,
)


mandarin_system_prompt_str = (
    "# 角色描述\n"
    "你是一位专业且富有同情心的护士。你的目标是模拟真实护士的查房，你要不停地询问患者的问题，通过多轮对话收集患者的详细信息，并提供有针对性的建议。\n"
    "你的目标受众是老年人。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。\n"
    "# 回答要求：\n"
    "请务必使用普通话进行回答！！！！ 请务必使用普通话进行回答！！！！\n"
    "上下文信息如下。\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "请根据上下文信息而不是先验知识来回答以下的查询。"
    "作为一个医疗人工智能助手，你的回答要尽可能严谨。请务必使用普通话进行回答！！！\n"
    "Query: {query_str}\n"
    "Answer: "
)

mandarin_system_prompt = PromptTemplate(mandarin_system_prompt_str)

yueyu_system_prompt_str = (
    "# 角色描述\n"
    "你是一位专业且富有同情心的护士。你的目标是模拟真实护士的查房，你要不停地询问患者的问题，通过多轮对话收集患者的详细信息，并提供有针对性的建议。\n"
    "你的目标受众是广东地区老年人，官方语言是粤语。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。\n"
    "# 回答要求：\n"
    "请务必使用粤语进行回答！！！！ 请务必使用粤语进行回答！！！！\n"
    "上下文信息如下。\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "请根据上下文信息而不是先验知识来回答以下的查询。"
    "作为一个医疗人工智能助手，你的回答要尽可能严谨。请务必使用粤语进行回答！！！\n"
    "Query: {query_str}\n"
    "Answer: "
)
yueyu_system_prompt = PromptTemplate(yueyu_system_prompt_str)

response_synthesizer = get_response_synthesizer(response_mode="tree_summarize",
                                                verbose=True,
                                                summary_template=yueyu_system_prompt
                                                )

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    # node_postprocessors=[
    #     LLMRerank(
    #         choice_batch_size=2,
    #         top_n=3,
    #     )
    # ],

)

react_chat_engine = index.as_chat_engine(chat_mode="react", verbose=True)

context_chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)

condense_question_chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine=query_engine,
    verbose=True,
)


chat_engine = index.as_chat_engine(
    chat_mode="best",
    verbose=True,
    similarity_top_k=10,
    # response_synthesizer=response_synthesizer,
    node_postprocessors=[
        LLMRerank(
            choice_batch_size=2,
            top_n=3,
        )
    ],
    response_mode="compact",
    text_qa_template=yueyu_system_prompt,
    # response_synthesizer=response_synthesizer
)

chat_engine_dict = {
    "default": chat_engine,
    "react": react_chat_engine,
    "context": context_chat_engine,
    "condense_question": condense_question_chat_engine
}


def chat_pipeline(user_query: str, history: List[Dict[str, Any]] = []):
    global chat_engine
    if len(history) > 0:
        for message in history:
            chat_engine.chat_history.append(ChatMessage(
                role=message['role'], content=message['content']))
    execution_start_time = time.time()
    response = chat_engine.chat(user_query)
    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)
    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def chat_stream_pipeline(user_query: str, history: List[Dict[str, Any]] = []):
    global chat_engine
    if len(history) > 0:
        for message in history:
            chat_engine.chat_history.append(ChatMessage(
                role=message['role'], content=message['content']))
    execution_start_time = time.time()
    streaming_response = chat_engine.stream_chat(user_query)
    # 打印 streaming_response 的所有属性和方法
    # print("streaming_response attributes:", dir(streaming_response))
    # print("streaming_response details:")
    # pprint(streaming_response)

    # for token in streaming_response.response_gen:
    #     # yield token
    #     print(token, end="")
    ref = []
    for reference in streaming_response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)
    non_streaming_response = {"reference": ref}
    yield json.dumps(non_streaming_response) + "\n\n"

    for token in streaming_response.response_gen:
        # print(token, end="")
        yield token
    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)


def condense_question_pipeline(user_query: str, history: List[Dict[str, Any]] = []):
    global condense_question_chat_engine
    if len(history) > 0:
        for message in history:
            condense_question_chat_engine.chat_history.append(ChatMessage(
                role=message['role'], content=message['content']))
    execution_start_time = time.time()
    response = condense_question_chat_engine.chat(user_query)
    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)

    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def context_chat_pipeline(user_query: str, history: List[Dict[str, Any]] = []):
    global context_chat_engine
    execution_start_time = time.time()
    if len(history) > 0:
        for message in history:
            context_chat_engine.chat_history.append(ChatMessage(
                role=message['role'], content=message['content']))
    response = context_chat_engine.chat(user_query)
    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)

    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def react_chat_pipeline(user_query: str, history: List[Dict[str, Any]] = []):
    global react_chat_engine
    if len(history) > 0:
        for message in history:
            react_chat_engine.chat_history.append(ChatMessage(
                role=message['role'], content=message['content']))
    execution_start_time = time.time()
    response = react_chat_engine.chat(user_query)
    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)

    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def query_pipeline(user_query: str):
    execution_start_time = time.time()
    response = query_engine.query(user_query)

    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)

    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def rag_chat_final_use(user_query, history, language="mandarin"):
    # 根据用户的查询以及回复(基本的寒暄是不需要的)，判断是否需要RAG
    global chat_engine, query_engine
    execution_start_time = time.time()
    # system_prompt = get_system_prompt("nurse")
    # chat_engine.chat_history.append(ChatMessage(
    #     role=MessageRole.SYSTEM, content=system_prompt))
    if history[-1].get('role', '') == 'user':
        history.pop()
    summary_template = query_engine.get_prompts()
    print("summary_template", summary_template)

    if language != "mandarin":
        query_engine.update_prompts(
            {"response_synthesizer:summary_template": yueyu_system_prompt}
        )
    response = query_engine.query(user_query)

    # chat_engine = chat_engine.from_llm(system_prompt=system_prompt)
#     role_description = f'''
# 请务必使用粤语,广东话进行回答！！！！ 请务必使用粤语,广东话进行回答！！！！
# '''
#     if len(chat_engine.chat_history) == 0 or chat_engine.chat_history[0] != 'system':
#         chat_engine.chat_history.append(ChatMessage(
#             role=MessageRole.SYSTEM, content=role_description))
#     for message in history:
#         chat_engine.chat_history.append(ChatMessage(
#             role=message['role'], content=message['content']))
#     print(chat_engine.chat_history)
#     response = chat_engine.chat(user_query)
    # response = query_engine.query(user_query)

    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        # print("reference", reference.metadata['file_name'])
        # print("reference", reference.text)
    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref

    # custom_chat_history = [
    #     ChatMessage(
    #         role=MessageRole.USER,
    #         content="Hello assistant, we are having a insightful discussion about Paul Graham today.",
    #     ),
    #     ChatMessage(role=MessageRole.ASSISTANT, content="Okay, sounds good."),
    # ]
    # chat_engine = chat_engine.from_defaults(
    #     chat_history=custom_chat_history,
    # )


def reset_chat_engine():
    global chat_engine
    chat_engine.reset()
    return {"message": "Chat engine has been reset"}


def get_chat_history():
    global chat_engine
    chat_history = chat_engine.chat_history
    print("chat_history", chat_history)
    return chat_history


def nursing_agent(user_query: str, history: List[Dict[str, Any]], is_stream=False) -> Dict[str, Any]:
    nursing_system_prompt = f'''
        # 角色描述
        你是一位专业且富有同情心的护士。你的目标是模拟真实护士的查房，你要不停地询问用户的问题，通过多轮对话收集{variables.get('patient_name', '患者')}的详细信息，并提供有针对性的建议。
        你的目标受众是老年人。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。

        # 任务
        1. 前面几轮对话中请主动寻找话题，和患者进行寒暄，确保建立良好的沟通氛围。
        2. 每次回复的内容不要太长，尽量使用口语化的回复。
        3. 根据老年人的具体反馈，提供切实可行的建议，并保持简洁，避免复杂术语。
        4. 在主动引导话题的同时，要善于倾听老年人的反馈和情感，并适时调整话题。
        5. 通过观察和老年人的反馈，识别他们的兴趣点（如阅读、爱好、日常习惯等），并引导他们分享这些信息，建立更深层次的互动。
        6. 在表达关心时，请结合实际行动（如提醒喝水、提供药物、建议休息等）来增强沟通效果。
        7. 尽量让老年人感受到被关注和支持，适时给予鼓励和安慰，帮助他们感到舒适和安全。
        '''
    return nursing_system_prompt


def single_agent(user_query: str, history: List[Dict[str, Any]], mode={"reply_style": "simple", "state": "objective"}, language="mandarin", is_stream=False) -> Dict[str, Any]:
    """Handles the single-agent conversation."""
    health_advisor_system = get_multi_style_prompt("nurse", mode, language)
    # insert system prompt into history
    if len(history) == 0 or history[0]['role'] != 'system':
        history.insert(0, {'role': 'system', 'content': health_advisor_system})
    # print("history length", len(history))
    # print("history", history)
    # Record user query in history
    # history.append({'role': 'user', 'content': user_query})
    # Call GPT-4
    if is_stream:
        async def response_generator():
            async for chunk in gpt4o_history_call_stream("gpt-4o-mini", history):
                yield chunk
        return response_generator()
    else:
        execution_start_time = time.time()
        response = gpt4o_history_call("gpt-4o-mini", history)
        history.append({'role': 'assistant', 'content': response})
        execute_end_time = time.time()
        execution_time = execute_end_time - execution_start_time
        return {'final_response': response, 'history': history, 'execution_time': execution_time}


def multi_agent(user_query: str, health_history: List[Dict[str, Any]], therapy_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Handles the multi-agent conversation for the first scenario."""

    temp = f'''
5. 如果患者表现出害怕、畏惧、恐慌等情绪，请先用一句话安抚患者的情绪，然后再提出一个问题，以更好地了解患者的情绪。
6. 如果认为患者连续几次回答都没有很好地描述病情，请提供选择题，以帮助患者更明确地表达症状。
7. 当确信已经足够了解病情后，给出人性化的建议。基于患者提供的信息，提供明确且可操作的指导。
'''

    health_advisor_system = f'''
# 角色描述
你是一位专业且富有同情心的医疗专家。你的目标是模拟真实医生的问诊，通过多轮对话收集患者的详细信息，并提供有针对性的建议。
你的目标受众是老年人。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解问题。

## 任务
- **探究患者的感受**：询问患者的具体症状和感受，让患者感到被理解。
- **提出澄清问题**：如果患者的陈述模糊或缺乏细节，请询问具体信息。
- **彻底调查症状**：询问症状的持续时间、强度和性质。
- **检查相关症状**：询问任何可能相关的症状。
- **回顾病史**：确保了解任何先前的诊断或治疗。
- **提供清晰指导**：基于提供的信息，给出明确且可操作的建议。
- **确保理解**：确认患者理解你的建议和指示。

## 输出要求
1. 每次只问一个问题，逐步思考，确保一次性提的问题不超过两个，并分点罗列。
2. 确保你的回答直接回应患者的问题，不要输出基本的寒暄。
3. 在每轮对话中表现出同情心和专业性，告诉患者他的感觉是正常的，并做出回应，让他知道医生在倾听，提供实际的支持。
4. 如果不确信已经足够了解病情，患者回答问题后请直接问下一个问题，以更好地了解病情。



## 示例对话：
```json
{{
  "用户输入": "我最近头疼得很厉害。",
  "模型回复": "我非常理解您的感受。我们来仔细看看这个问题。\\n您的头疼已经持续多长时间了？",
  "用户回答": "大概有一周了。",
  "模型回复": "谢谢您的信息。让我们进一步了解一下。\\n您的头疼是轻微、中等还是严重呢？",
  "用户回答": "中等偏重。",
  "模型回复": "我能理解您的感受。这个过程对您来说真的很不容易。让我们再详细了解下\\n这种头疼的性质是什么？是钝痛、刺痛还是压迫感？",
  "用户回答": "刺痛。",
  "模型回复": "谢谢您的描述。我们再看看其他可能的症状。\\n有没有伴随其他症状，比如恶心、呕吐或者视力模糊？",
  "用户回答": "有时会感到恶心。",
  "模型回复": "明白了。这些信息非常有帮助。请不要担心，我会尽力帮助您。\\n您最近是否有过任何压力、睡眠不足或身体不适的情况？"
}}
'''

    # therapy_system = f'''你是一位心理健康咨询师。你的任务是提供情绪管理和共情支持。请根据健康助手的回复，添加共情和情绪支持的内容，帮助患者缓解焦虑和期待情绪，使最终回复更具关怀和支持性。'''
    therapy_system = f'''
    # 角色：
    - 你是一位心理健康咨询师，你的目标受众是老年人，你的任务是基于健康助手的回复为患者提供情绪管理和共情支持。
    # 任务：
    1. 根据健康助手的回复，用合适并且自然的语气解释给老年人，要让老年人能够理解你的关心和支持。
    2. 不要过多润色，保持简洁明了。
    3. 流程：第一步是探究患者的感受，第二步是回应，告诉患者他的感觉是正常的，让他安心，对患者的话语做出反应，让他知道医生在倾听：
    # 输出要求：
    1. 改写的内容尽量要少，不要过多润色，保持简洁明了。
    2. 语气要自然
    3. 对于不用改写的情况，直接输出健康助手的回复！！！
    '''
    if len(health_history) == 0:
        health_history.append(
            {'role': 'system', 'content': health_advisor_system})
    if len(therapy_history) == 0:
        therapy_history.append({'role': 'system', 'content': therapy_system})
    # gpt-4o-mini
    # Record user query in health advisor history
    health_history.append({'role': 'user', 'content': user_query})
    health_advice = gpt4o_history_call("gpt-4o-mini", health_history)
    health_history.append({'role': 'assistant', 'content': health_advice})

    therapy_template = f'''
    请基于下面健康助手的回复，为患者提供情绪支持和共情。你的回复应当帮助患者缓解焦虑的情绪，使患者感受到关怀和支持。
    只需稍微修改健康助手的内容，增加一点点共情和支持的语气。
    健康助手回复：{health_advice}
'''

    therapy_history.append({'role': 'user', 'content': therapy_template})
    therapy_advice = gpt4o_history_call("gpt-4o-mini", therapy_history)
    therapy_history.append({'role': 'assistant', 'content': therapy_advice})

    return {
        'final_response': therapy_advice,
        'health_history': health_history,
        'therapy_history': therapy_history
    }


def emotion_detection(text):
    # 期待，焦虑，中性
    # emotion_list = ['positive', 'negative', 'neutral']
    emotion_list = ['期待', '焦虑', '中性']
    system_prompt = f"""
    在医院预问诊过程中，了解患者的情绪状态有助于医生更好地了解患者的心理和身体状况。情绪可能影响患者的症状描述和医疗需求。因此，准确识别患者的情绪对于提供高质量的医疗服务至关重要。
    你是一个医院预问诊的情绪识别助手，专门从患者提供的文本中判断情绪。你的任务是分析患者的陈述，识别其情绪，并输出情绪列表中的情绪和对应的置信度。
    情绪列表：
    {', '.join(emotion_list)}

    要求：
    1. 从患者的文本中判断其情绪，并只输出情绪列表中的情绪。
    2. 对每个识别出的情绪，提供一个0到1之间的置信度分数，表示你对该情绪判断的确定程度。
    3. 请输出对应的json格式。
    示例：
    患者陈述： “我最近总是觉得非常紧张，晚上睡不着觉。”
    输出：
    {{
    "情绪": "焦虑",
    "置信度": 0.85
    }}
    """
    emotion_judge = json.loads(gpt4o_call(
        "gpt-4o-mini", text, system_prompt, True))
    print("emotion_judge", type(emotion_judge), emotion_judge)
    return emotion_judge

    # from nltk.sentiment.vader import SentimentIntensityAnalyzer
    # sia = SentimentIntensityAnalyzer()
    # # 3. Sentiment Classification:
    # # Calculate overall sentiment score based on the extracted features and context information
    # sentiment_scores = sia.polarity_scores(text)
    # # Determine the sentiment polarity based on the sentiment scores
    # if sentiment_scores['compound'] >= 0.05:
    #     sentiment_polarity = 'positive'
    # elif sentiment_scores['compound'] <= -0.05:
    #     sentiment_polarity = 'negative'
    # else:
    #     sentiment_polarity = 'neutral'


def check_rag_usage(user_query, history):
    # 根据用户的查询以及回复(基本的寒暄是不需要的)，判断是否需要RAG
    symbol = False
    if len(history) < 2:
        return False
    # 判断逻辑
    rag_usage_system_prompt = f'''
你是一个RAG（Retrieval-Augmented Generation）使用助手。在医院的预问诊过程中，你的任务是帮助用户理解他们的健康问题。RAG模型结合了检索和生成能力，可以为用户提供更准确和全面的回答。
背景信息：在医院预问诊过程中，RAG模型特别适合处理需要具体医学知识、复杂背景信息或特定医疗数据的问题。例如，当用户描述的症状需要详细的医学解释或当现有对话无法提供足够信息时，RAG模型可以提供帮助。
具体任务：请仔细分析以下用户的查询和历史对话，并判断是否需要使用RAG模型来生成回复。你的回答应该只包含“True”或“False”。
'''
    input_prompt = f'''
用户查询：{user_query}
历史对话：{history}
'''
    rag_usage_response = gpt4o_call(
        "gpt-4o-mini", input_prompt, rag_usage_system_prompt)

    return rag_usage_response


def keywords_highlight(user_query, bald_text):
    prompt_template = f'''
    请从以下文本中提取与用户查询最相关且优先级最高的关键词。确保关键词直接与用户查询相关，并且对理解主要内容至关重要。
    用户查询: {user_query}
    文本内容: {bald_text}
    输出要求: 提供一个包含所有相关关键词的 JSON 格式的列表，按重要性排序。不需要包含任何额外信息或评论。

    示例输出:
    {{
        "keywords": ["高血压", "治疗", "生活方式改变", "药物治疗"]
    }}
    '''
    system_prompt = '''你是一个提取关键词的专家，你可以从给定的文本中提取与用户查询相关的关键词及重要信息。确保关键词高度相关，并根据其与查询的相关性进行优先级排序。
    '''
    highlight_text = gpt4o_call(
        "gpt-4o", prompt_template, system_prompt, json=True)

    # 解析返回的 JSON 格式的字符串
    try:
        keywords_list = json.loads(highlight_text).get("keywords", [])
    except json.JSONDecodeError:
        # 如果返回的内容不是有效的 JSON 格式，则使用正则表达式提取关键词
        keywords_list = re.findall(r'\d+\.\s*(.*?)(?:\n|$)', highlight_text)
        keywords_list = [keyword.strip()
                         for keyword in keywords_list]  # 去除多余的空格

    return keywords_list


def history_summary(history):
    # 生成历史对话的摘要
    history_summary_system_prompt = f'''
    你是一个对话摘要生成助手。在医院预问诊过程中，你的任务是帮助用户理解他们的健康问题。你需要根据用户的查询和历史对话，生成一个简洁的对话摘要，以帮助用户快速回顾对话内容。
    请根据以下历史对话生成一个简洁的对话摘要。确保摘要简明扼要，包含对话的主要内容和重要信息。此外，请在摘要的最后添加一条建议或注意事项，以帮助用户进一步关注健康问题。
    '''
    history = str(history)
    history_summary_response = gpt4o_call(
        "gpt-4o-mini", history, history_summary_system_prompt)

    return history_summary_response


if __name__ == "__main__":
    test_summary_history = [
        {"role": "user", "content": "我最近血压一直很高，感觉头痛。请查查资料"},

    ]

    # summary = history_summary(test_summary_history)
    # print("history_summary response:", summary)

    print("\nTesting rag_final_use:")
    user_query = '我最近血压一直很高，感觉头痛。请查查资料'
    rag_response, ref = rag_chat_final_use(
        user_query, test_summary_history, "yueyu")
    print("rag_final_use response:", rag_response)
    print("ref_length:", len(ref))
    print("rag_final_use references:", ref)

    # 测试单代理
    print("\nTesting single_agent:")
    user_query = "我今天又带你不舒服，血压有点高"
    # user_query = "你好，最近感冒了，有什么要注意的，请按照markdown格式回答"
    # user_query = "您好，最近很久没有人来看我了"
    history = [{'role': 'user', 'content': user_query}]
    single_agent_response = single_agent(user_query, 
                                         history,
                                         mode={"reply_style": "simple", "state": "objective"},
                                         language="mandarin")
    print("single_agent response:", single_agent_response)

    # 测试多代理
    print("\nTesting multi_agent:")
    health_history = []
    therapy_history = []
    # multi_agent_response = multi_agent(
    #     user_query, health_history, therapy_history)
    # print("multi_agent response:", multi_agent_response)

    # # 测试情绪检测
    # print("\nTesting emotion_detection:")
    # text = "我最近总是觉得非常紧张，晚上睡不着觉。"
    # emotion_detection_response = emotion_detection(text)
    # # print("emotion_detection response:", emotion_detection_response)

    # # 测试RAG使用检查
    # print("\nTesting check_rag_usage:")
    # history = [
    #     {'role': 'user', 'content': "我最近头疼得很厉害。"},
    #     {'role': 'assistant', 'content': "你头疼持续了多久？"}
    # ]
    # user_query = "请问LLM是什么？"
    # check_rag_usage_response = check_rag_usage(user_query, history)
    # # print("check_rag_usage response:", check_rag_usage_response)

    # # 测试关键词高亮
    # print("\nTesting keywords_highlight:")
    # bald_text = "高血压是一种常见的慢性病，治疗包括生活方式改变和药物治疗。"
    # keywords_highlight_response = keywords_highlight(user_query, bald_text)
    # # print("keywords_highlight response:", keywords_highlight_response)

    # # 测试 chatPipeline
    # print("\nTesting chatPipeline:")
    # chat_pipeline_response, chat_pipeline_ref = chat_pipeline(user_query)
    # # print("chatPipeline response:", chat_pipeline_response)
    # # print("chatPipeline references:", chat_pipeline_ref)

    # print("\nTesting chatPipeline round 2:")
    # round2_user_query = "LLM怎么解决幻觉问题"
    # chat_pipeline_response, chat_pipeline_ref = chat_pipeline(
    #     round2_user_query)
    # # print("chatPipeline response:", chat_pipeline_response)
    # # print("chatPipeline references:", chat_pipeline_ref)

    # 测试 ragPipeline
    # print("\nTesting ragPipeline:")
    # rag_pipeline_response, rag_pipeline_ref = query_pipeline(user_query)
    # print("ragPipeline response:", rag_pipeline_response)
    # print("ragPipeline references:", rag_pipeline_ref)

    # # 获取聊天历史记录
    # print("\nGetting chat history:")
    # chat_history = get_chat_history()
    # print("Chat history:", chat_history)

    # # 重置 chat_engine
    # print("\nResetting chat engine:")
    # reset_response = reset_chat_engine()
    # print(reset_response)

    # # 测试 condense_question_pipeline
    # print("\nTesting condense_question_pipeline:")
    # condense_question_response, condense_question_ref = condense_question_pipeline(
    #     user_query)
    # # print("condense_question_pipeline response:", condense_question_response)
    # # print("condense_question_pipeline references:", condense_question_ref)

    # # 测试 context_chat_pipeline
    # print("\nTesting context_chat_pipeline:")
    # context_chat_response, context_chat_ref = context_chat_pipeline(user_query)
    # # print("context_chat_pipeline response:", context_chat_response)
    # # print("context_chat_pipeline references:", context_chat_ref)

    # # 测试 react_chat_pipeline
    # print("\nTesting react_chat_pipeline:")
    # react_chat_response, react_chat_ref = react_chat_pipeline(user_query)
    # # print("react_chat_pipeline response:", react_chat_response)
    # # print("react_chat_pipeline references:", react_chat_ref)

    # # 测试 rag_chat_final_use
    # print("\nTesting rag_chat_final_use:")
    # history = [{'role': 'user', 'content': "我最近头疼得很厉害。"},
    #            {'role': 'assistant', 'content': "你头疼持续了多久？"}]
    # rag_chat_final_response, rag_chat_final_ref = rag_chat_final_use(
    #     "请问LLM是什么？", history)
    # # print("rag_chat_final_use response:", rag_chat_final_response)
    # # print("rag_chat_final_use references:", rag_chat_final_ref)
