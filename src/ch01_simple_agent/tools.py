import requests
import os
from tavily import TavilyClient

# 根据城市查询天气
def get_weather(city: str):
    url = f'https://wttr.in/{city}?format=j1'
    
    try:
        # 发起网络请求
        response = requests.get(url)
        response.raise_for_status() # 检查响应状态码是否为200
        data = response.json() # 解析响应
        
        # 提取天气
        # print(data)
        # print(data['data']['current_condition'])
        current_condition = data['data']['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']
        
        return f'{city}当前天气：{weather_desc}，气温{temp_c}摄氏度.'
        
        
    except requests.exceptions.RequestException as e:
        return f'错误：查询天气时遇到网络问题 - {e}'
    except (KeyError, IndexError) as e:
        return f'错误：解析天气数据失败，可能是城市名无效 - {e}'

# 根据城市和天气搜索推荐旅游景点
def get_attraction(city: str, weather: str):
    
    # 1. 获取环境变量
    api_key = os.getenv("TAVILY_KEY")
    if not api_key:
        return "错误：未配置 TAVILY_KEY 环境变量"
    
    # 2. 初始化客户端
    tavily = TavilyClient(api_key=api_key)
    
    query = f"'{city}' 在'{weather}'天气最值得去的旅游景点推荐及理由"
    
    try:
        # 4. 调用API include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query,search_depth='basic',include_answer=True)
        
        # 5. Tavily返回的结果已经非常干净，可以直接使用
        if response.get("answer"):
            return response['answer']
        # 如果没有综合性回答，则按照格式化输出
        formatted_results = []
        for result in response.get("results",[]):
            formatted_results.append(f"- {result['title']}: {result['coontent']}") 
            
        if not formatted_results:
            return "抱歉：没有找到相关的旅游景点推荐。"
        return "根据搜索，为你找到以下信息：\n"+"\n".join(formatted_results)
    except Exception as e:
        return f"错误：执行Tavily搜索时出现错误 - {e}"
    
    

available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction
}