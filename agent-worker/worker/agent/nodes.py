from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from worker.agent.state import AgentState
from worker.agent.prompt_loader import load_prompt
from worker.agent.tools import ALL_TOOLS

MAX_HISTORY = 10

_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    max_tokens=256,
    temperature=0.7,
)

# Solo bindea tools si hay alguna definida
llm = _llm.bind_tools(ALL_TOOLS) if ALL_TOOLS else _llm

# Solo instancia ToolNode si hay tools
tool_node = ToolNode(ALL_TOOLS) if ALL_TOOLS else None


async def generate_response(state: AgentState) -> AgentState:
    system_prompt = await load_prompt("whatsapp")
    messages = (
        [SystemMessage(content=system_prompt)]
        + state["messages"][-MAX_HISTORY:]
        + [HumanMessage(content=state["user_text"])]
    )
    response = await llm.ainvoke(messages)
    return {
        "response": response.content,
        "messages": [HumanMessage(content=state["user_text"]), response],
    }


def should_use_tools(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"