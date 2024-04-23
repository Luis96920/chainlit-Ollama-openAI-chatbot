from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from chainlit.input_widget import Select, Switch, Slider
import chainlit as cl

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate # type: ignore
from langchain_openai import ChatOpenAI # type: ignore

@cl.set_chat_profiles
async def chat_profile():

    return [
        cl.ChatProfile(
            name="GPT-3.5",
            markdown_description="The underlying LLM model is **GPT-3.5**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="GPT-4",
            markdown_description="The underlying LLM model is **GPT-4**.",
            # icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="mixtral-8x7b-32768",
            markdown_description="The underlying LLM model is **Mixtral-8x7b**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="gemma-7b-it",
            markdown_description="The underlying LLM model is **Gemma-7b**.",
            # icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="llama3-8b-8192",
            markdown_description="The underlying LLM model is **Llama3-8b**.",
            # icon="https://picsum.photos/200",
        ),

    ]

@cl.on_chat_start
async def on_chatstart():
    
    # # Sending an image with the local file path
    # elements = [
    # cl.Image(name="image1", display="inline", path="groq.jpeg")
    # ]
    # await cl.Message(content="Hello there, I am Groq. How can I help you ?", elements=elements).send()

    model_selected = cl.user_session.get("chat_profile")
    
    if 'gpt' in model_selected.lower():
        vendor_name = "OpenAI"
        apikey_html =  "https://platform.openai.com/api-keys"
    else:
        vendor_name = "Groq"
        apikey_html = "https://console.groq.com/keys"

    await cl.Message(
        content=f"To chat with the LLM **{model_selected}**, type your query in below textbox. Please make sure you have proper **[{vendor_name}]({apikey_html})** API key set in .env file."
    ).send()

    # Setting up the LLM
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable Machine Learning Engineer.",
            ),
            ("human", "{question}"),
        ]
    )

    # Groq avaialble models: https://console.groq.com/settings/limits
    if 'gpt' not in model_selected.lower():
        model = ChatGroq(temperature=0, model_name=model_selected)
        # runnable = prompt | model | StrOutputParser()
        # cl.user_session.set("runnable", runnable)
    elif '3.5' in model_selected.lower():
        # https://platform.openai.com/docs/models/overview
        model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    elif '-4' in model_selected.lower():
        model = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


    
@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
