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
from langchain_community.llms import Ollama

from langchain_google_vertexai import VertexAI

@cl.set_chat_profiles
async def chat_profile():

    return [
        cl.ChatProfile(
            name="GPT-3.5 on OpenAI remote",
            markdown_description="The underlying large language model model is **GPT-3.5**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="GPT-4 on OpenAI remote",
            markdown_description="The underlying large language model model is **GPT-4**.",
            # icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="Mixtral-8x7b on Groq remote",
            markdown_description="The underlying large language model model is **Mixtral-8x7b**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Gemma-7b on Groq remote",
            markdown_description="The underlying large language model model is **Gemma-7b**.",
            # icon="https://picsum.photos/250",
        ),
        cl.ChatProfile(
            name="Llama3-8b on Groq remote",
            markdown_description="The underlying large language model model is **Llama3-8b**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Llama3 on local",
            markdown_description="The underlying large language model model is **Llama3-8b quantization 4-bit**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Gemma on local",
            markdown_description="The underlying large language model model is **Gemma 9B quantization 4-bit**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Phi-3 mini on local",
            markdown_description="The underlying large language model model is **Phi-3 mini 4B quantization 4-bit**.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="CodeGemma on local",
            markdown_description="The underlying large language model model is **Gemma 9B** tuned for coding assistance with quantization 4-bit.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Deepseek-coder on local",
            markdown_description="The underlying large language model model is **deepseek-coder 1B** for coding assistance with quantization 4-bit.",
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
    
    gcp_project_ID = "aihub123-test1"

    if 'gpt' in model_selected.lower():
        vendor_name = "OpenAI"
        apikey_html =  "https://platform.openai.com/api-keys"
    else:
        vendor_name = "Groq"
        apikey_html = "https://console.groq.com/keys"

    await cl.Message(
        content=f"You are chatting with LLM **{model_selected.split()[0]}** via {model_selected.split()[2]}."
    ).send()

    # Setting up the large language model
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
    if 'local' in model_selected.lower():
        if 'llama3' in model_selected.lower():
            # 4.7GB (https://ollama.com/library)
            model = Ollama(model="llama3")
        elif 'gemma' in model_selected.lower():
            # 5.0GB
            model = Ollama(model="gemma")
        elif 'codegemma' in model_selected.lower():
            # 5.0GB
            model = Ollama(model="codegemma")
        elif 'phi' in model_selected.lower():
            # 2.3GB
            model = Ollama(model="phi3")
        elif 'deepseek-coder' in model_selected.lower():
            # ~800MB
            model = Ollama(model="deepseek-coder")
    elif 'gpt' not in model_selected.lower() and 'groq' in model_selected.lower():
        if 'gemma' in model_selected.lower():
            model = ChatGroq(temperature=0, model_name='gemma-7b-it')
        elif 'mixtral' in model_selected.lower():
            model = ChatGroq(temperature=0, model_name='mixtral-8x7b-32768')
        elif 'llama' in model_selected.lower():
            model = ChatGroq(temperature=0, model_name='llama3-8b-8192')
        else:
            print("model not found")
    elif 'gpt' in model_selected.lower() and '3.5' in model_selected.lower():
        # https://platform.openai.com/docs/models/overview
        model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    elif 'gpt' in model_selected.lower() and '-4' in model_selected.lower():
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
