from .base import Tool
from typing import Any, Callable,Dict
from hello_agents import ToolRegistry

class ToolRegistry:
    def __init__(self):
        self._tools = dict[str, Tool] = {}
        self._functions = dict[str, dict[str,Any]] = {}

    def register_tool(self, tool: Tool):
        if tool.name in self._tools:
            print(f"⚠️ 警告:工具 '{tool.name}' 已存在，将被覆盖。")
        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已注册。")
        
    def register_function(self,name: str,decription: str,func: Callable[[str],str]):
        """
        直接注册函数作为工具（简便方式）

        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """
        if name in self._functions:
            print(f"⚠️ 警告:工具 '{name}' 已存在，将被覆盖。")

        self._functions[name] = {
            "description": decription,
            "func": func
        }
        print(f"✅ 工具 '{name}' 已注册。")
        
        
    def get_tools_descriptions(self) -> str:
        """
        获取所有工具的描述，用于提示用户可用的工具
        """
        descriptions = []
        
        # 获取tools的描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
            
        # 获取functions的描述
        for name, func_info in self._functions.items():
            descriptions.append(f"- {name}: {func_info['description']}")

        return "\n".join(descriptions) if descriptions else "没有可用工具。"
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """"
        """
        return None
    def execute_tool(self, name: str, input_text: str) -> str:
        """
        执行工具

        Args:
            name: 工具名称
            input_text: 输入参数

        Returns:
            工具执行结果
        """
        # 优先查找Tool对象
        if name in self._tools:
            tool = self._tools[name]
            try:
                # 简化参数传递，直接传入字符串
                return tool.run({"input": input_text})
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        # 查找函数工具
        elif name in self._functions:
            func = self._functions[name]["func"]
            try:
                return func(input_text)
            except Exception as e:
                return f"错误：执行工具 '{name}' 时发生异常: {str(e)}"

        else:
            return f"错误：未找到名为 '{name}' 的工具。"