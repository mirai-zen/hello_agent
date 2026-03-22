from typing import Dict,Any

from dotenv import load_dotenv
from .tools.tool import search

class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str,Dict[str, Any]] = {}
        
    def registerTool(self, name: str, description: str, func: callable):
        if name in self.tools:
            print(f'告警：工具 "{name}" 已存在，将被覆盖。')
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")
        
    def getTool(self, name: str)-> callable:
        return self.tools.get(name,{}).get("func")
    
    def getAvailableTools(self) -> str:
        return '\n'.join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])
        

if __name__ == "__main__":
    # 加载配置
    load_dotenv()


    exec = ToolExecutor()
    
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及你的知识库中找不到的信息时，应使用该工具。"
    exec.registerTool("Search", search_description, search)
    
    # 打印可用的工具
    print(f"\n ---- 可用工具 -----")
    print(exec.getAvailableTools)
    
    # 测试工具可用性
    print(f"\n ------ 测试工具可用性 -----")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"
    
    tool_func = exec.getTool(tool_name)
    if tool_func:
        observation = tool_func(tool_input)
        print("---- 观察 (Observation)")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")
    