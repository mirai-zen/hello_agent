
from ..core import Agent, HelloAgentsLLM,Config,Message
from ..tools import ToolRegistry
from typing import List, Optional, Tuple,Dict
import re

MY_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么行动。
Action: 选择一个行动，格式必须是以下之一:
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循:工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动:
"""

class ReActAgent(Agent):
    def __init__(
            self, 
            name: str, 
            llm: HelloAgentsLLM, 
            tool_registry: ToolRegistry, 
            system_prompt: Optional[str] = None, 
            config: Optional[Config] = None,
            max_steps: int = 5,
            custom_prompt: Dict[str:str] = None
        ):
        super.__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history:List[str] = []
        self.prompt_template = custom_prompt or MY_REACT_PROMPT

    def run(self, input_text: str, **kwargs) -> str:
        self.current_history = []
        current_step = 0
        
        print(f"\n🤖 {self.name} 开始处理问题: {input_text}")
        
        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 步骤 {current_step} ---")
            
            # 1. 构建提示词
            tool_descriptions = self.tool_registry.get_tool_descriptions()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tool_descriptions,
                question=input_text,
                history=history_str
            )

            # 2. 调用LLM
            message = [{'role':"user", "content":prompt}]
            response = self.llm.invoke(message)

            # 3. 解析响应
            thought, action = self._parse_output(response)
            # 4. 检查完成条件
            if action and action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                self.add_message(Message(input_text, "user"))
                self.add_message(Message(final_answer, "assistant"))
                return final_answer
            # 5. 执行工具调用
            if action:
                tool_name, tool_input = self._parse_action(action)
                observation = self.tool_registry.execute_tool(tool_name, tool_input)
                # 更新历史
                self.current_history.append(f"Action: {action}")
                self.current_history.append(f"Observation: {observation}")
        # 达到最大步数
        final_answer = "抱歉，我无法在限定步数内完成这个任务。"
        self.add_message(Message(input_text, "user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer


    def _parse_output(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析LLM输出，提取思考和行动"""
        thought_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)
        
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        
        return thought, action
    
    def _parse_action(self, action_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析行动文本，提取工具名称和输入"""
        match = re.match(r"(\w+)\[(.*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
    def _parse_action_input(self, action_text: str) -> str:
        """解析行动输入"""
        match = re.match(r"\w+\[(.*)\]", action_text)
        return match.group(1) if match else ""