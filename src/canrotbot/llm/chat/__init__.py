from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.messages import AnyMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools.base import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from nonebot import get_plugin_config

from ..config import LLMConfig
from ..tools import get_tools
from ..trim import TrimConfig, trim_messages
from .config import OpenAIConfig
from .model import ChatContext, context_aware_system_prompt

global_config = get_plugin_config(LLMConfig)
trim_config = get_plugin_config(TrimConfig)
openai_config = get_plugin_config(OpenAIConfig)

_model: BaseChatModel | None = None
_agent: CompiledStateGraph | None = None
_mcp_client = MultiServerMCPClient(global_config.mcp_config)


def get_model():
    global _model

    if _model is None:
        _model = ChatOpenAI(
            model=openai_config.model,
            base_url=openai_config.base_url,
            api_key=openai_config.api_key,
            extra_body=openai_config.extra_body,
        )

    return _model


async def get_agent():
    global _agent

    available_tools: list[BaseTool] = []

    if global_config.enable_tools:
        available_tools += get_tools()
    if global_config.enable_mcp:
        available_tools += await _mcp_client.get_tools()

    if _agent is None:
        middleware = [context_aware_system_prompt]

        # trim message middleware
        if trim_config.method == "trim":
            middleware.append(trim_messages(trim_config.trim_keep))
        elif trim_config.method == "summarize":
            middleware.append(
                SummarizationMiddleware(
                    model=get_model(),
                    trigger=trim_config.summarize_trigger,
                    keep=trim_config.summarize_keep,
                )
            )

        _agent = create_agent(
            model=get_model(),
            tools=available_tools,
            middleware=middleware,  # type: ignore
            context_schema=ChatContext,
        )

    return _agent


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
