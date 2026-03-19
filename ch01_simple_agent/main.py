

# 提示词
import os
import re
from dotenv import load_dotenv
from AIClient import OpenAICompatiblaClient
from tools import available_tools


SYSTEM_PROMPT = """
你是一个只能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具
- `get_weather(city: str)`：查询指定城市的实时天气。
- `get_attraction(city: str, weather: str)`：根据城市和天气搜索推荐的旅游景点。

# 行动格式
你的回答必须严格遵守以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次恢复只输出一对Thought-Action:
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成：
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用`finish(answer="...")`来输出答案。

请开始吧。
"""


if __name__ == "__main__":
    load_dotenv() # 加载 env 配置
    # print(get_weather("shanghai"))
    # print(get_attraction("",""))
    
    llm = OpenAICompatiblaClient(
        model=os.getenv("MODEL"),
        api_key=os.getenv("ALBAILIAN_API_KEY"),
        base_url=os.getenv("ALBAILIAN_BASE_URL")
    )
    
    prompt = "你好，请帮我查询一下今天深圳的天气，然后根据天气推荐一个合适的旅游景点。"
    prompt_history = [f"用户请求：{prompt}\n"+"="*40]
    
    
    # Loop 
    for i in range(5): 
        print(f"--------循环 {i+1} ----------\n")
        
        # 3.1 调用模型思考
        full_prompt = "\n".join(prompt_history)
        
        llm_output = llm.generate(full_prompt,system_prompt=SYSTEM_PROMPT)
        
        match = re.search(r'(Thought:.*?ACTION:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)',llm_output,re.DOTALL)
        if match:
            truncated = match.group(1).strip()
            if truncated != llm_output.strip():
                llm_output = truncated
                print("已经截断多余的 Thought-Action 对")
        print(f"模型输出：\n{llm_output}\n")
        prompt_history.append(llm_output)
        

        # 3.2 解析并执行行动
        action_mathc = re.search(r"Action:(.*)",llm_output,re.DOTALL)
        if not action_mathc:
            print("解析错误：模型输出中未找到 Action。")
            break
        action_str = action_mathc.group(1).strip()
        
        if action_str.startswith("finish"):
            final_answer = re.search(r'finish\(answer="(.*)"\)',action_str).group(1)
            print(f"任务完成，最终答案：{final_answer}")
            break
        
        tool_name = re.search(r"(\w+)\(",action_str).group(1)
        args_str = re.search(r"\((.*)\)",action_str).group(1)
        kwargs = dict(re.findall(r'(\w+)="([^"]*)"',args_str))
        
        if tool_name in available_tools:
            observation = available_tools[tool_name](**kwargs)
        else:
            observation = f"错误：未定义工具 '{tool_name}'"
            
        # 3.3 记录观察结果
        observation_str = f"Observation: {observation}"
        print(f'{observation_str}\n'+"="*40)
        prompt_history.append(observation_str)
            

            

    
    

