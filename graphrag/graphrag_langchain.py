
# 我想将该路径添加到项目路径中，从而可以在当前文件运行py文件
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import FAISS
from models import embedding_vllm
from utils import get_similar_entity
import re 
from pydantic import BaseModel, Field
from utils import create_structured_chain
from langchain_core.tools import tool

eval_prompt = """
# 指令
请评估如下问题对应的知识图谱输出答案是否正确，如果正确则输出True 如果不符合则输出False
要给出这么判断的理由

# 问题：
{query}

# 知识图谱输出的答案：
{answer}

# 输出：
"""

llm_qwen_14b = ChatOpenAI(model="text2sql2", #   Qwen2.5-14B
                    base_url='http://172.31.24.111:33071/v1', 
                    api_key='EMPTY',
                    temperature=0,
                    )
class GradeBaseModel(BaseModel):
    grade: bool = Field(default=False, description="根据用户问题判断知识图谱输出的答案是否正确")
    
grade_prompt = PromptTemplate(
template=eval_prompt, 
input_variables=["query",  "answer"]
)



grade_chain = create_structured_chain(
        prompt=grade_prompt,
        model=llm_qwen_14b,
        structured_data=GradeBaseModel
    )

uri = 'bolt://172.31.24.111:7687'  # 
username = "neo4j"                  # 默认用户名
password = "liucd123"    # 替换为你的实际密码

graph = Neo4jGraph(url=uri, username=username, password=password, enhanced_schema=True,)
print(graph.schema)




CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:
# How many people played in Top Gun?
MATCH (m:Movie {{name:"Top Gun"}})<-[:ACTED_IN]-()
RETURN count(*) AS numberOfActors

The question is:
{question}

modify_entity:
{modify_str}

cypher: 
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question", "modify_str"], template=CYPHER_GENERATION_TEMPLATE
)


chain = GraphCypherQAChain.from_llm(
    llm_qwen_14b,
    graph=graph, 
    verbose=True, 
    return_direct=True,
    top_k = 10,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
    return_intermediate_steps=True,
    # validate_cypher=True,
    allow_dangerous_requests=True
    )

question = "我今年得了高血压，饮食上应该注意什么"

pattern = r'\(\s*(?:\w+\s*:)?\s*(?:\s*:)?(\w+)\s*\{[^}]*name\s*:\s*["\']([^"\']+)["\']'
vector = FAISS.load_local("faiss_index_entity", embedding_vllm,  allow_dangerous_deserialization=True)


@tool
def medical_graphrag(question):
    """当需要查询疾病相关知识时才使用此工具."""
    try:
        response = chain.invoke({"query": question, "modify_str": ''})
        cypher = response['intermediate_steps'][0]['query']
        result = response['result']

    except Exception as e:
        result = []
        cypher = ''


    if result == []:
        """如果是语义对齐的问题"""
        print('开启语义对齐 ...')
        matches = re.findall(pattern, cypher)
        print(matches) # [('Disease', '脑中风'), ('Symptom', '咳嗽'), ('AnotherLabel', '测试名称')]

        modify = []
        for data in matches:
            query = data[0]
            value = data[1]
            search_docs = vector.similarity_search(value, k=3, filter={"source": query})
            
            docs_list = [doc.page_content for doc in search_docs]
            if docs_list[:1] == [value]:
                continue

            modify.append(f"将原始实体做更正：将原始的实体{value} 更改为--> {docs_list} 其中的含义最相似的一个")
        modify_str = '\n'.join(modify)
        
        response = chain.invoke({"query": question, "modify_str": modify_str})
        result = response['result']

    if result: # 如果不为空，则要大模型评估其正确性
        response = grade_chain.invoke({'query': question, 'answer': result})
        
        grade = response.grade

    print('图谱输出：', result)
    print('大模型评估结果', grade)
    
    
    if grade:
        return {'query': question, "result": result} 
    else:
        return {'query': question, "result": ''}


# 感冒的死亡率是多少

# MATCH (d:Disease)-[:common_drug|recommand_drug]->(drug:Drug {name: '松栢速效救心丸'})
# RETURN d

if __name__ == '__main__':
    medical_graphrag('感冒的治愈率是多少')