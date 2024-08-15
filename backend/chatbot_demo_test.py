from service import (chat_pipeline, condense_question_pipeline,
                     context_chat_pipeline, react_chat_pipeline,
                     chat_stream_pipeline, rag_chat_final_use,
                     rag_chat_final_use, reset_chat_engine, single_agent,multi_agent)


if __name__ == "__main__":
    print("\nTesting single_agent:")
    user_query = "你好，最近感冒了，有什么要注意的，请按照markdown格式回答"
    history = []
    single_agent_response = single_agent(user_query, history)
    # print("single_agent response:", single_agent_response)

    # 测试多代理
    print("\nTesting multi_agent:")
    health_history = []
    therapy_history = []
    multi_agent_response = multi_agent(
        user_query, health_history, therapy_history)
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
