from langchain_openai import ChatOpenAI



llm_chatgpt = ChatOpenAI(model="gpt-3.5-turbo",temperature=0, api_key='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')
llm_deepseek = ChatOpenAI(model="deepseek-chat",
                    base_url='https://api.deepseek.com',
                    api_key='sk-84dd90701fe6471696cf24136d340a74',
                    temperature=0,
                    )

llm_qwen_plus = ChatOpenAI(model="qwen-plus",
                    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                    api_key='sk-4e27d583808849128b07458af74724a6',
                    temperature=0,
                    )
