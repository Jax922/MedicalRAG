from service import (chat_pipeline, condense_question_pipeline,
                     context_chat_pipeline, react_chat_pipeline,
                     chat_stream_pipeline, rag_chat_final_use,
                     rag_chat_final_use, reset_chat_engine, single_agent, multi_agent)

def start_conversation():
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

        # 调用 single_agent 函数处理历史记录，并传递当前历史
        response = single_agent(user_query, history)

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
    start_conversation()
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
