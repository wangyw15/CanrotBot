from langchain.agents import create_agent
from langchain.messages import AnyMessage, HumanMessage
from langchain_core.tools.base import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from nonebot import get_plugin_config

from ..config import LLMConfig
from ..tools import get_tools
from .config import OpenAIConfig
from .model import ChatContext, context_aware_system_prompt

global_config = get_plugin_config(LLMConfig)
openai_config = get_plugin_config(OpenAIConfig)

_openai_model = ChatOpenAI(
    model=openai_config.model,
    base_url=openai_config.base_url,
    api_key=openai_config.api_key,
    extra_body=openai_config.extra_body,
)
_mcp_client = MultiServerMCPClient(global_config.mcp_config)
_openai_agent = None


def get_model():
    return _openai_model


async def get_agent():
    global _openai_agent

    available_tools: list[BaseTool] = []

    if global_config.enable_tools:
        available_tools += get_tools()
    if global_config.enable_mcp:
        available_tools += await _mcp_client.get_tools()

    if _openai_agent is None:
        _openai_agent = create_agent(
            model=_openai_model,
            tools=available_tools,
            middleware=[context_aware_system_prompt],  # type: ignore
            context_schema=ChatContext,
        )
    return _openai_agent


async def summarize_context(messages: list[AnyMessage]) -> str:
    agent = await get_agent()
    response = await agent.ainvoke(
        {
            "messages": [
                *messages,
                HumanMessage(
                    "Summarize the subject of the conversation in a descriptive format with no more than 10 words in the above language"
                ),
            ]
        }
    )
    return response["messages"][-1].content
