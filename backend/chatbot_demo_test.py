# from service import (chat_pipeline, condense_question_pipeline,
#                      context_chat_pipeline, react_chat_pipeline,
#                      chat_stream_pipeline, rag_chat_final_use,
#                      rag_chat_final_use, reset_chat_engine, single_agent, multi_agent,
#                      get_multi_style_prompt,single_agent_v1_2)

from typing import List, Dict, Any
import time
from utils import gpt4o_history_call
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv("../env/.env"), override=True)


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


def single_agent_v1_2(user_query: str, history: List[Dict[str, Any]], mode={"reply_style": "simple", "state": "objective"}, language="mandarin", is_stream=False) -> Dict[str, Any]:
    v1_2_system_prompt = f'''
# 角色描述
你是一位专业且富有同情心的护士。你的目标是模拟真实的聊天，你要不停地询问老人问题，通过多轮对话收集老人的详细信息，并提供有针对性的建议。
你的目标受众是老年人。你需要在对话中表现出同情心和专业性，你的回答要简单易懂，帮助老年患者迅速理解。
# 任务
1. 前面几轮对话中请主动寻找话题，和老人进行寒暄，确保建立良好的沟通氛围。
2. 每次回复的内容不要太长，尽量使用口语化的回复。
3. 根据老年人的具体反馈，提供切实可行的建议，并保持简洁，避免复杂术语。
4. 在主动引导话题的同时，要善于倾听老年人的反馈和情感
5. 通过观察和老年人的反馈，识别他们的兴趣点（如阅读、爱好、日常习惯等），并引导他们分享这些信息，建立更深层次的互动。
6. 为了更好地表达关心与同理心，务必要关注老人的感受，适时地表达对他们情感的理解与共鸣，从而增强信任感和亲切感。同时，结合实际行动（如温柔地提醒喝水、细心提供药物、贴心建议休息等）可以进一步提升沟通效果，使关怀更加具体和有温度
7. 尽量让老年人感受到被关注和支持，适时给予鼓励和安慰，帮助他们感到舒适和安全。
'''
    if len(history) == 0 or history[0]['role'] != 'system':
        history.insert(0, {'role': 'system', 'content': v1_2_system_prompt})
    execution_start_time = time.time()
    response = gpt4o_history_call("gpt-4o-mini", history)
    history.append({'role': 'assistant', 'content': response})
    execute_end_time = time.time()
    execution_time = execute_end_time - execution_start_time
    return {'final_response': response, 'history': history, 'execution_time': execution_time}


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


def start_conversation(style):
    print("开始与AI护士进行对话。如果要结束对话，请输入'退出'。")
    history = []

    while True:
        # 获取用户输入
        user_query = input("你: ")

        # 如果用户输入 '退出'，则结束对话
        if user_query.lower() in ['退出', 'exit', 'quit']:
            print("对话结束。")
            break

        # 直接将用户输入加入到 history 中
        history.append({'role': 'user', 'content': user_query})
        print(history)
        # 调用 single_agent 函数处理历史记录，并传递当前历史
        response = single_agent_v1_2(user_query, history, style)

        # 更新 history，保持对话的延续性（注意此时 single_agent 会自动添加 AI 回复）
        history = response['history']

        # 打印AI护士的回复
        print(f"AI护士: {response['final_response']}\n")

    # 对话结束后，打印历史记录
    print("\n对话历史记录：")
    for entry in history:
        role = "你" if entry['role'] == 'user' else "AI护士"
        print(f"{role}: {entry['content']}")


if __name__ == "__main__":

    style = {"reply_style": "simple", "state": "passive"}
    # print(get_multi_style_prompt("nurse", style))
    start_conversation(style)
    # print("\nTesting single_agent:")
    # user_query = "我今天又带你不舒服，血压有点高"
    # history = []
    # single_agent_response = single_agent(user_query, history)
    # # print("single_agent response:", single_agent_response)

    # # 测试多代理
    # print("\nTesting multi_agent:")
    # health_history = []
    # therapy_history = []
    # multi_agent_response = multi_agent(
    #     user_query, health_history, therapy_history)
    # print("multi_agent response:", multi_agent_response)
    # user_query = 'what is LLM'
    # print("\nTesting chat_stream_pipeline:")

    # # 运行生成器函数并打印结果
    # response_generator = chat_stream_pipeline(user_query)
    # try:
    #     # 获取初始非流式响应
    #     initial_response = next(response_generator)
    #     print("Initial Response:", initial_response)

    #     # 获取流式响应
    #     for response in response_generator:
    #         print("Stream Response:", response)
    # except StopIteration:
    #     pass
