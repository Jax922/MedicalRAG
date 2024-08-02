import argparse
import json
import os
from typing import Any, Dict, List

from dotenv import find_dotenv, load_dotenv
from utils import gpt4o_call, gpt4o_history_call

os.environ['HF_HOME'] = './model'
# print(os.environ['HF_HOME'])
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

_ = load_dotenv(find_dotenv("../env/.env"))


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

def get_health_advisor_prompt():
    health_advisor_prompt = f'''
    你将扮演一个医院的全科医生，你需要针对病人的初始描述提出3-5个问题以更好的了解病人的病情，当你确信已经足够了解后请给出人性化的建议。
    请注意：
    - 每次只问一个问题
    - 如果你不确信已经足够了解病人病情，病人回答问题后请直接问下一个问题，以更好的了解病情；
    - 如果病人表现出害怕，畏惧、恐慌等情绪时，你先需要使用一句话安抚病人的情绪，并在下一句话提出一个问题，以更好的了解病人情绪。
    - 如果认为患者连续几次回答都没有很好地描述病情，请给病人选择题。这可以帮助引导患者更明确地表达他们的症状。
    - 当确信已经足够了解患者的病情后，请给出人性化的建议。基于患者提供的信息，给出明确且可操作的指导。
    '''
    return health_advisor_prompt

def single_agent(user_query: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Handles the single-agent conversation."""
    system_prompt = f'''
    # 你是一位专业且富有同情心的医疗专家。你的目标是模拟真实医生的问诊，是通过多轮对话，收集患者的详细信息，并提供有针对性的建议。
    # 你的目标受众是老年人。你需要在对话中表现出同情心和专业性，简单易懂，确保你的回答既有关怀性又具有科学性。
    # 任务：
    - 提出澄清问题：如果患者的陈述模糊或缺乏细节，请询问具体信息。
    - 彻底调查症状：询问症状的持续时间、强度和性质。
    - 检查相关症状：询问任何可能相关的症状。
    - 回顾病史：确保了解任何先前的诊断或治疗。
    - 提供清晰指导：基于提供的信息，给出明确且可操作的建议。
    - 确保理解：确认患者理解你的建议和指示。
    # 输出要求：
    1. 请在每轮对话中表现出同情心和专业性，确保你的回答既有关怀性又具有科学性。
    2. 请不要输出基本的寒暄，确保你的回答直接回应患者的问题。
    3. 请逐步思考
    4. 请一次性聚焦于一个方面的问题，不要一次性提太多方面的问题。
    '''
    initialize_history('health_advisor', history, system_prompt)
    # Record user query in history
    history.append({'role': 'user', 'content': user_query})
    # Call GPT-4
    response = gpt4o_history_call("gpt-4o-mini", history)
    history.append({'role': 'assistant', 'content': response})
    return {'final_response': response, 'history': history}


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


def multi_agent(user_query: str, health_history: List[Dict[str, Any]], therapy_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Handles the multi-agent conversation for the first scenario."""
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
    initialize_history('health_advisor', health_history, health_advisor_system)
    initialize_history('therapy_advisor', therapy_history, therapy_system)
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


def multi_agent_v2(user_query: str, health_history: List[Dict[str, Any]], therapy_history: List[Dict[str, Any]], comprehensive_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Handles the multi-agent conversation for the second scenario."""
    health_advisor_system = f'''你是一位健康助手。你的任务是提供关于疾病和健康问题的专业信息和建议。请根据患者的描述，解释健康问题的原因、常见症状、治疗建议和注意事项。'''
    therapy_system = f'''你是一位心理健康咨询师。你的任务是提供情绪管理和共情支持。你需要根据用户的回复，表现出足够多的关怀性，帮助患者缓解焦虑和期待情绪。'''
    comprehensive_response_system = f'''你是一位综合响应代理。你的任务是整合健康助手和心理健康咨询师的回复，生成最终的综合回复。请在参考健康助手提供的专业信息和心理健康咨询师提供的情绪支持后，生成一份既有专业性又具有人性化关怀的综合回复。你的回复应当帮助患者理解健康问题，并提供情感上的支持与安慰，使患者感受到关怀和支持。'''

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

    return {
        'final_response': comprehensive_response,
        'health_history': health_history,
        'therapy_history': therapy_history,
        'comprehensive_history': comprehensive_history
    }


def interactive_cli():
    parser = argparse.ArgumentParser(
        description="Multi-agent conversation tester")
    parser.add_argument("--version", type=int, choices=[
                        1, 2], default=1, help="Specify the multi-agent version to use (1 or 2)")

    args = parser.parse_args()
    version = args.version

    health_history = []
    therapy_history = []
    comprehensive_history = []

    while True:
        user_query = input("请输入您的问题（输入'q'结束对话）：")
        if user_query.lower() == 'q':
            break
        if version == 1:
            result = multi_agent(user_query, health_history, therapy_history)
        else:
            result = multi_agent_v2(
                user_query, health_history, therapy_history, comprehensive_history)

        final_response = result['final_response']
        health_history = result.get('health_history', [])
        therapy_history = result.get('therapy_history', [])
        comprehensive_history = result.get('comprehensive_history', [])

        print("\n最终回复:", final_response)
        print("\n健康助手历史记录:", json.dumps(
            health_history, ensure_ascii=False, indent=2))
        print("\n心理健康咨询师历史记录:", json.dumps(
            therapy_history, ensure_ascii=False, indent=2))
        if version == 2:
            print("\n综合响应代理历史记录:", json.dumps(
                comprehensive_history, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    interactive_cli()
