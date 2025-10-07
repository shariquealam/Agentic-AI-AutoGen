import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

os.environ[
    "OPENAI_API_KEY"] = "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"


async def main1():
    print( "I am inside function" )

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o" )
    assistant = AssistantAgent( name="assistant", model_client=model_client )
    await Console( assistant.run_stream( task="What is 25 * 8?" ) )
    await model_client.close()


asyncio.run( main1() )
