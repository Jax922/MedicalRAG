import json
import os
import time
from typing import Any, Dict, List
from dotenv import find_dotenv, load_dotenv
from llama_index.core import (Settings, SimpleDirectoryReader,
                              StorageContext, VectorStoreIndex,
                              get_response_synthesizer,
                              load_index_from_storage)
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai_like import OpenAILike
from utils import gpt4o_call

_ = load_dotenv(find_dotenv("../env/.env"))


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


# 初始化全局 chat_engine 和 index
index = setup_and_load_index()
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=10,
    verbose=True,
)

response_synthesizer = get_response_synthesizer(response_mode="tree_summarize",
                                                verbose=True)

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[
        LLMRerank(
            choice_batch_size=2,
            top_n=2,
        )
    ],
)

chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine=query_engine,
    verbose=True,
)


def ragPipeline(user_query: str):
    execution_start_time = time.time()
    response = query_engine.query(user_query)

    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        print("reference", reference.metadata['file_name'])
        print("reference", reference.text)

    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def chatPipeline(user_query: str):
    global chat_engine
    execution_start_time = time.time()
    response = chat_engine.chat(user_query)
    ref = []
    for reference in response.source_nodes:
        ref.append([reference.text, reference.metadata['file_name']])
        print("reference", reference.metadata['file_name'])
        print("reference", reference.text)
    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    print("Execution Time:", execution_time)

    return response.response, ref


def reset_chat_engine():
    global chat_engine
    chat_engine.reset()
    return {"message": "Chat engine has been reset"}


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
