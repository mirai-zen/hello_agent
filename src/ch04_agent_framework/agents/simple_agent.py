from ..core import Config, Message, HelloAgentsLLM,Agent
# from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from typing import Optional

class MySimpleAgent(Agent):
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_registry: Optional['ToolRegistry'] = None,
        enable_tool_calling: bool = True
    ):
        super().__init__(name,llm,system_prompt,config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        print(f"✅️ {name} 初始化完成，工具调用：{'启用' if self.enable_tool_calling else '禁用'}")
    
    def run(self,input_text: str, max_tool_iterations: int = 3, **kwargs) -> str:
        print(f"🤖 {self.name} 正在处理：{input_text}")
        
        # 构建消息体
        message = []
        
        # 添加系统消息(可能包含工具信息)
        enhanced_system_prompt = self._get_enhanced_system_prompt()
        message.append({'role': "system","content": enhanced_system_prompt})
        
        # 添加历史消息
        for msg in self._history:
            message.append({"role":msg.role,"content":msg.content})
            
        # 添加当前用户消息
        message.append({"role": "user", "content": input_text})
        
        # 如果没用启用工具调用，使用简单对话逻辑
        if not self.enable_tool_calling:
            response = self.llm.invoke(message,**kwargs)
            self.add_message(Message(input_text,"user"))
            print(f"✅️ {self.name} 响应完成")
            return response
        
        # 支持多轮工具调用的逻辑
        return self.__run