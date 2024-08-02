import json
import os
import pprint
import time
from typing import Any, Dict, List

from agentlego import list_tools, load_tool
from dotenv import find_dotenv, load_dotenv
from llama_index.core import (PromptTemplate, Settings, SimpleDirectoryReader,
                              StorageContext, VectorStoreIndex,
                              get_response_synthesizer,
                              load_index_from_storage)
from llama_index.core.chat_engine import (CondensePlusContextChatEngine,
                                          CondenseQuestionChatEngine)
from llama_index.core.indices.query.query_transform.base import \
    HyDEQueryTransform
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.postprocessor import LLMRerank, SimilarityPostprocessor
from llama_index.core.query_engine import (CustomQueryEngine,
                                           RetrieverQueryEngine,
                                           TransformQueryEngine)
from llama_index.core.response_synthesizers import BaseSynthesizer
from llama_index.core.retrievers import BaseRetriever, VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.llms.openai_like import OpenAILike
from openai import OpenAI
from llama_index.core.retrievers import AutoMergingRetriever

from utils import (encode_image, gpt4o_call, gpt4o_history_call,
                   gpt4o_image_call, local_image_to_data_url, tool_list)

os.environ['HF_HOME'] = './model'
# print(os.environ['HF_HOME'])
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

_ = load_dotenv(find_dotenv("../env/.env"))

# embedding 用本地bge-large-zh/en


def testCustomLLM():
    # delete v1
    # api_base = os.getenv("QWEN_BASE_URL")[0:-3]
    # print(api_base)
    # 必须要指定是chat model
    def testQwen():
        print("testQwen")
        test_llm = OpenAILike(api_base=os.getenv("QWEN_BASE_URL"),
                              api_key=os.getenv("QWEN_API_KEY"),
                              model="qwen-max",
                              is_chat_model=True,
                              timeout=300)
        # print(test_llm)
        text = "What is the weather?"
        print("answer:", test_llm.complete(text))
        completions = test_llm.stream_complete("Paul Graham is ")
        for completion in completions:
            print(completion.delta, end="")
    testQwen()


def reactChatEngine():

    return


def HydeQueryTransform():
    start_load_time = time.time()
    Settings.llm = OpenAILike(
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        is_chat_model=True)
    # Settings.embed_model = HuggingFaceEmbedding(model_name="bge-large-zh")
    Settings.embed_model = OpenAIEmbedding(
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-3-small")

    # build index
    documents = SimpleDirectoryReader("./data").load_data()
    # embed_model = Settings.embed_model
    # need meta data
    # index = VectorStoreIndex.from_documents(documents, show_progress=True)
    # index.storage_context.persist(persist_dir="./storage")

    # 检查存储目录是否存在
    if not os.path.exists("./storage"):
        print("存储目录不存在，创建新的索引...")
        # 创建新的索引并从文档中加载
        index = VectorStoreIndex.from_documents(
            documents,
            show_progress=True,
        )
        # 持久化存储上下文
        index.storage_context.persist(persist_dir="./storage")
        print("索引创建并保存到 ./storage 目录。")

    else:
        print("存储目录已存在，加载现有索引...")
        # 从默认的存储上下文加载现有的索引
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        # 如果在初始化索引时使用了自定义的 transformations、embed_model 等选项，
        # 则在 load_index_from_storage 期间需要传入相同的选项，或者将其设置为全局设置。
        index = load_index_from_storage(storage_context)
        print("索引已从 ./storage 目录加载。")

    # # Load the index from the storage
    # index = load_index_from_storage(storage_context)

    end_load_time = time.time()
    load_time = end_load_time - start_load_time
    print("Load Time:", load_time)

    # configure retriever
    # retriever = index.as_retriever()
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10,
        verbose=True,

    )

    # configure response synthesizer
    # which mode to use:
    response_synthesizer = get_response_synthesizer(response_mode="tree_summarize",
                                                    verbose=True)

    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[
            LLMRerank(
                choice_batch_size=5,
                top_n=2,
            )
        ],
        # node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.1)],
    )
    # hyde
    hyde = HyDEQueryTransform(include_original=True)
    hyde_query_engine = TransformQueryEngine(query_engine, hyde)
    user_query = '''What did the article say about LLM? 
    Please list them in layers and points, and bold the important parts'''
    hyde_response = hyde_query_engine.query(user_query)
    for reference in hyde_response.source_nodes:
        # ref.append(reference.text)
        print("hyde_reference", reference.text)
    return


def chatEngine():
    return


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
    输出要求: 提供一个包含所有相关关键词的列表，按重要性排序。不需要包含任何额外信息或评论。
    '''
    system_prompt = '''你是一个提取关键词的专家，你可以从给定的文本中提取与用户查询相关的关键词及重要信息。确保关键词高度相关，并根据其与查询的相关性进行优先级排序。
    '''
    highlight_text = gpt4o_call("gpt-4o", prompt_template, system_prompt)
    return highlight_text

# 1.用户 -> 健康助手 ->  心理健康咨询师 -> 心理健康咨询师生成最终回复 -> 用户
# 2.用户 -> 健康助手 + 心理健康咨询师 -> 综合响应Agent -> 综合响应Agent生成最终回复 -> 用户


def initialize_history(agent_role: str, history: List[Dict[str, Any]], system_content: str):
    if not history:
        history.append({'role': 'system', 'content': system_content})


def multi_agent(user_query: str, health_history: List[Dict[str, Any]], therapy_history: List[Dict[str, Any]]) -> str:
    """Handles the multi-agent conversation for the first scenario."""
    health_advisor_system = '你是一位健康助手。你的任务是提供关于疾病和健康问题的专业信息和建议。请根据患者的描述，解释健康问题的原因、常见症状、治疗建议和注意事项。'
    therapy_system = '你是一位心理健康咨询师。你的任务是提供情绪管理和共情支持。请根据健康助手的回复，添加共情和情绪支持的内容，帮助患者缓解焦虑和期待情绪，使最终回复更具关怀和支持性。'

    initialize_history('health_advisor', health_history, health_advisor_system)
    initialize_history('therapy_advisor', therapy_history, therapy_system)

    # Record user query in health advisor history
    health_history.append({'role': 'user', 'content': user_query})
    health_advice = gpt4o_history_call("gpt-4o-mini", health_history)
    health_history.append({'role': 'assistant', 'content': health_advice})

    therapy_template = f'''
    请基于下面健康助手的回复，为患者提供情绪支持和共情。你的回复应当帮助患者缓解焦虑和期待情绪，使患者感受到关怀和支持。
    请不要对健康助手的内容做太多修改，而是在其基础上添加情绪支持和共情内容。
    健康助手回复：{health_advice}'''

    therapy_history.append({'role': 'user', 'content': therapy_template})
    therapy_advice = gpt4o_history_call("gpt-4o-mini", therapy_history)
    therapy_history.append({'role': 'assistant', 'content': therapy_advice})

    return therapy_advice, health_history, therapy_history


def multi_agent_v2(user_query: str, health_history: List[Dict[str, Any]], therapy_history: List[Dict[str, Any]], comprehensive_history: List[Dict[str, Any]]) -> str:
    """Handles the multi-agent conversation for the second scenario."""
    health_advisor_system = f'''你是一位健康助手。你的任务是提供关于疾病和健康问题的专业信息和建议。请根据患者的描述，解释健康问题的原因、常见症状、治疗建议和注意事项。
    '''
    therapy_system = f'''你是一位心理健康咨询师。你的任务是提供情绪管理和共情支持。你需要根据用户的回复，表现出足够多的关怀性，帮助患者缓解焦虑和期待情绪，'''
    comprehensive_response_system = f'''你是一位综合响应代理。你的任务是整合健康助手和心理健康咨询师的回复，生成最终的综合回复。
请在参考健康助手提供的专业信息和心理健康咨询师提供的情绪支持后，生成一份既有专业性又具有人性化关怀的综合回复。你的回复应当帮助患者理解健康问题，并提供情感上的支持与安慰，使患者感受到关怀和支持。
'''

    initialize_history('health_advisor', health_history, health_advisor_system)
    initialize_history('therapy_advisor', therapy_history, therapy_system)
    initialize_history('comprehensive_response',
                       comprehensive_history, comprehensive_response_system)

    # Record user query in health advisor history
    health_history.append({'role': 'user', 'content': user_query})
    health_advice = gpt4o_history_call("gpt-4o-mini", health_history)
    health_history.append({'role': 'assistant', 'content': health_advice})

    # Record health advisor's advice in therapy advisor history
    therapy_history.append({'role': 'user', 'content': user_query})
    therapy_advice = gpt4o_history_call("gpt-4o-mini", therapy_history)
    therapy_history.append({'role': 'assistant', 'content': therapy_advice})

    # Record comprehensive response
    comprehensive_template = f'''
    你是一个综合响应代理。你的任务是整合健康助手和心理健康咨询师的回复，生成最终的综合回复。确保回复既有专业性又具有人性化关怀，需要帮助患者理解健康问题，并提供情感上的支持与安慰，使患者感受到关怀和支持。
    用户问题：{user_query}
    健康助手回复：{health_advice}
    心理健康咨询师回复：{therapy_advice}
'''
    comprehensive_history.append(
        {'role': 'user', 'content': comprehensive_template})
    comprehensive_response = gpt4o_history_call(
        'gpt-4o-mini', comprehensive_history)
    comprehensive_history.append(
        {'role': 'assistant', 'content': comprehensive_response})

    return comprehensive_response, health_history, therapy_history, comprehensive_history


def role_play_single_doctor():
    # Role playing 可以参看langGPT的写法
    # 或者需要规定 Task Persona Context examples Format Tone
    role_play = ['simple', 'empathetic']
    simple_system_prompt = f'''
    请简明扼要地解释患者的病情、治疗方案和下一步措施。你的主要职责是：展示理解并向患者提供清晰明了的信息。
    '''
    empathetic_response_system_prompt = f'''
    你是一位富有同情心且知识渊博的健康顾问，专注于老年护理。你的主要职责是：
    1. 提出详细的后续问题，以全面了解患者的情况。
    2. 在每个回复中展示同情心和理解。
    3. 根据患者的独特情况提供个性化和具体的建议。

    始终牢记这些责任：
    - 积极倾听并回应患者的情感和身体需求。
    - 确保每个回复都针对患者的具体问题和情况量身定制。
    - 在整个对话中保持专业和关怀的语气。
    '''
    pre_hint_prompt = f'''
    1. 确保询问更多细节，以全面了解患者的情况。
    2. 在回复中展示同情心和理解。
    3. 提供具体且个性化的建议，避免使用泛泛的回答。
    '''
    post_hint_prompt = f'''
    1. 询问更多细节以确保获得全面的信息。
    2. 确保每个回复都针对患者的具体问题和情况量身定制。
    3. 根据情况提供具体的建议。
    '''


def initialize_settings(api_base, api_key, model, embed_model):
    Settings.llm = OpenAILike(
        api_base=api_base,
        api_key=api_key,
        model=model,
        is_chat_model=True
    )
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


def ragPipeline():
    index = setup_and_load_index()
    # configure retriever
    # retriever = index.as_retriever()
    # base_retriever = base_index.as_retriever(similarity_top_k=6)
    # retriever = AutoMergingRetriever(base_retriever, storage_context, verbose=True) 
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10,
        verbose=True,
    )

    # configure response synthesizer
    # which mode to use:
    response_synthesizer = get_response_synthesizer(response_mode="tree_summarize",
                                                    verbose=True)

    # assemble query engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[
            LLMRerank(
                choice_batch_size=5,
                top_n=2,
            )
        ],
        # node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.1)],
    )

    user_query = '''What did the article say about LLM? 
    Please list them in layers and points, and bold the important parts'''
    # query
    # direct retrieve and test
    # node_postprocessors = [
    #     KeywordNodePostprocessor(
    #         required_keywords=["Combinator"], exclude_keywords=["Italy"]
    #     )
    # ]
    # query_engine = RetrieverQueryEngine.from_args(retriever, node_postprocessors=node_postprocessors)
    # query_result = retriever.retrieve(user_query)
    # print("query_result", query_result[0].text)
    execution_start_time = time.time()
    response = query_engine.query(user_query)
    pprint.pprint(response)
    ref = []
    for reference in response.source_nodes:
        # pprint.pprint(reference)
        ref.append(reference.text)
        print("reference", reference.metadata['file_name'],reference.text)
    # pprint.pprint(response.source_nodes[0].text)
    # print("--------------------------------------------")
    # print("type", type(response))
    # print("response", response)
    # pprint.pprint(response)

    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)


def quickTest():
    start_time = time.time()
    index = setup_and_load_index()
    # high level
    query_engine = index.as_query_engine(
        # response_mode="tree_summarize",
        verbose=True,
    )
    response = query_engine.query(
        "What is LLM")
    print(response)
    end_time = time.time()
    print("Execution Time:", end_time - start_time)
    return query_engine


def llamaAgent():
    return


def ragEvaluation():
    # Grouth Truth: 指人工标注的正确答案，利用这个实体可以对生成的答案进行分析，从而得到评估结果，
    # 在 LlamaIndex 中，这个实体叫做 Reference Answer

    print("RAG Evaluation Done")


def graphRAG():
    start_load_time = time.time()
    # Settings.llm = OpenAI(
    #     api_base=os.getenv("OPENAI_BASE_URL"),
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     model="gpt-4o-mini")

    Settings.llm = OpenAILike(
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        is_chat_model=True)
    # Settings.embed_model = HuggingFaceEmbedding(model_name="bge-large-zh")
    Settings.embed_model = OpenAIEmbedding(
        api_base=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model="text-embedding-3-small")

    Settings.chunk_size = 512

    return


if __name__ == "__main__":
    # quickTest()
    # testCustomLLM()
    ragPipeline()
    # emotion_detection("医生我最近有点失眠，怎么办？")
