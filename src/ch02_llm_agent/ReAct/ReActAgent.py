from dotenv import load_dotenv

from ch02_llm_agent.hello_agents_llm import HelloAgentsLLM
from ReAct.prompt import SYSTEM_PROMPT_TEMPLATE
from ReAct.toolExecutor import ToolExecutor
from ReAct.tools.tool import search
import re



class ReActAgent:
    def __init__(self,llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5 ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []
        
    def run(self, question: str):
        self.history = [] # 每次运行时重置历史记录
        current_step = 0
        
        while current_step < self.max_steps:
            current_step += 1
            print(f"----- 第 {current_step} 步 -----")
            
            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            
            prompt = SYSTEM_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )
            
            # 2. 调用 LLM 思考
            messages = [{"role": "user","content": prompt}]
            
            res_text = self.llm_client.think(messages=messages)
            if not res_text:
                print("错误: LLM未能返回有效响应")
                break
            
            # 3. 解析 LLM 输出
            thought, action = self._parse_output(res_text)
            if thought :
                print(f"思考： {thought}")
                
            if not action:
                print("告警: 未能解析出有效的Action, 流程中止。")
                break
            
            # 4. 执行Action
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)\]", action).group(1)
                print(f"最终答案：{final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                continue
            
            print(f"行动： {tool_name}[{tool_input}]")
            
            tool_func = self.tool_executor.getTool(tool_name)
            if not tool_func:
                observation = f"错误：未找到名为 '{tool_name}' 的工具"
            else:
                observation = tool_func(tool_input)
                
            print(f"观察: {observation}")
            
            # 将本轮的action 和 observation 添加到历史记录中
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")
        
        # 循环结束
        print("已达到最大步数，流程终止。")
        return None
            
        
            

# (这些方法是 ReActAgent 类的一部分)
    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。"""
        thought_match = re.search(r"Thought: (.*)", text)
        action_match = re.search(r"Action: (.*)", text)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。"""
        match = re.match(r"(\w+)\[(.*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        return None, None
    

if __name__ == "__main__":
    load_dotenv()
    llmClient = HelloAgentsLLM()

    exec = ToolExecutor()
    
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及你的知识库中找不到的信息时，应使用该工具。"
    exec.registerTool("Search", search_description, search)

    agent = ReActAgent(llm_client=llmClient,tool_executor=exec)
    res = agent.run("华为最新发布是手机是什么型号？")
    print(res)