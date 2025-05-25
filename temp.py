a = {
  "type": "agent",
  "response": {
    "messages": [
      {
        "content": "你是一个AI助手，请以简洁的方式回复用户，尽量不要超过100字。",
        "additional_kwargs": {},
        "response_metadata": {},
        "type": "system",
        "name": None,
        "id": "31f9f69e-af28-4b20-bf1f-ae2e789dfe5c"
      },
      {
        "content": "我的狗找不到了，我该怎么办",
        "additional_kwargs": {},
        "response_metadata": {},
        "type": "human",
        "name": None,
        "id": "70184c8d-3de8-4bf0-819c-58679bfe647e",
        "example": False
      },
      {
        "content": "您可以尝试以下几步：\n1. 返回您最后看到狗狗的地方，看看是否能找到它。\n2. 在您的社区或社交媒体上发布寻狗启事，包括狗狗的照片和描述。\n3. 联系当地的宠物收容所，看看是否有您的狗狗的信息。\n4. 如果可能的话，可以在您认为狗狗可能会去的地方张贴寻狗启事。\n希望您的狗狗能尽快回家。如果有其他需要帮助的地方，请告诉我。",
        "additional_kwargs": {
          "refusal": None
        },
        "response_metadata": {
          "token_usage": {
            "completion_tokens": 92,
            "prompt_tokens": 603,
            "total_tokens": 695,
            "completion_tokens_details": None,
            "prompt_tokens_details": None
          },
          "model_name": "Qwen2.5-14B",
          "system_fingerprint": None,
          "id": "chatcmpl-d093210391e249e3a338a4985f177e54",
          "finish_reason": "stop",
          "logprobs": None
        },
        "type": "ai",
        "name": None,
        "id": "run-9efa6823-5996-4b05-b02a-64c2eb3b3f6f-0",
        "example": False,
        "tool_calls": [],
        "invalid_tool_calls": [],
        "usage_metadata": {
          "input_tokens": 603,
          "output_tokens": 92,
          "total_tokens": 695,
          "input_token_details": {},
          "output_token_details": {}
        }
      }
    ]
  },
  "cost_time": 3.3811514377593994
}

print(a['response']['messages'][-1]['content'])