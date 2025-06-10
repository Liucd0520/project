# 我想将该路径添加到项目路径中，从而可以在当前文件运行py文件
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from langchain.prompts import PromptTemplate
from function_guide.prompt import prompt_function_guide
from models import llm_qwen_14b
from fp4nt import Fp4NT
from langchain_core.output_parsers import JsonOutputParser, ListOutputParser, CommaSeparatedListOutputParser
from langchain.output_parsers import EnumOutputParser
import pandas as pd 
from typing import List
import config  

guide_prompt = PromptTemplate(
    template=prompt_function_guide, 
    input_variables=["function_module", "function_tag", "query"]
    )

guide_chain = guide_prompt | llm_qwen_14b | CommaSeparatedListOutputParser()

fp4nt = Fp4NT(row_fill_merged=True, col_fill_merged=False, fill_mark='无')
df = fp4nt.build_excel_frame(config.function_path)
function_module = df.to_markdown(index=False)


async def recommand_function(query) -> List:

    param_input = {
        "function_module": function_module,
        "function_tag": config.function_tag,
        "query": query, 
        }
    func_tags =  await guide_chain.ainvoke(param_input)
    
    # 真实标签与取输出标签的交集，避免输出结果里含有非一级功能标签
    output_tags = list(set(func_tags).intersection(set(config.function_tag)))
    
    return output_tags 

if __name__ == "__main__":

    query_list = [
    "像找一个离家近的养老机构",  # 养老机构
    "怎么在软件上付养老院的费用啊", # 养老机构，我的
    "怎么找帮忙打扫家里卫生的阿姨？", # 居家服务
    "难过/心情不好/想找人说说话", # 居家服务 
    "找人陪我去医院 ",  # 健康医疗，居家服务
    ]

    for query in query_list:
        result =  recommand_function(query=query)
        print(result)