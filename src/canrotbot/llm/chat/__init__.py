from langchain.agents import create_agent
from langchain.messages import AnyMessage, HumanMessage
from langchain_openai import ChatOpenAI
from nonebot import get_plugin_config

from ..config import LLMConfig
from ..tools import get_tools
from .config import OpenAIConfig

global_config = get_plugin_config(LLMConfig)
openai_config = get_plugin_config(OpenAIConfig)
openai_model = ChatOpenAI(
    model=openai_config.model,
    base_url=openai_config.base_url,
    api_key=openai_config.api_key,
)
openai_agent = create_agent(
    model=openai_model,
    tools=get_tools() if global_config.enable_tools else [],
    system_prompt=global_config.system_prompt,
)


def get_agent():
    return openai_agent


async def summarize_context(messages: list[AnyMessage]) -> str:
    response = await get_agent().ainvoke(
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
