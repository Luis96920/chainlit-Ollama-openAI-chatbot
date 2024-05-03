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
            name="Llama3-70b on Groq remote",
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
        
        cl.ChatProfile(
            name="Wizard-math on local",
            markdown_description="The underlying large language model model is **deepseek-coder 1B** for coding assistance with quantization 4-bit.",
            # icon="https://picsum.photos/200",
        ),
        cl.ChatProfile(
            name="Qwen on local",
            markdown_description="The underlying large language model model is **qwen 4B** wtih quantization 4-bit.",
            # icon="https://picsum.photos/200",
        ),
    ]

@cl.on_chat_start
async def on_chatstart():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Role",
                label="Agent Role",
                values=["General Knowledge Expert", "Generative AI Expert", "DevOps Expert", "Mathematician"],
                initial_index=0,
            ), 
            Slider(
                id="Temperature",
                label="LLM Temperature",
                initial=0.1,
                min=0,
                max=1,
                step=0.1,
            ),
        ]
    ).send()

    model_selected = cl.user_session.get("chat_profile")
    

    await cl.Message(
        content=f"You are chatting with LLM **{model_selected.split()[0]}** via {model_selected.split()[2]}."
    ).send()

    # Setting up the large language model
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"You are a very knowledgeable {settings['Role']}.",
            ),
            ("human", "{question}"),
        ]
    )

    # Groq avaialble models: https://console.groq.com/settings/limits
    if 'local' in model_selected.lower():
        if 'llama3' in model_selected.lower():
            # 4.7GB (https://ollama.com/library)
            model = Ollama(model="llama3", temperature=settings["Temperature"])
        elif 'gemma' in model_selected.lower():
            # 5.0GB
            model = Ollama(model="gemma")
        elif 'codegemma' in model_selected.lower():
            # 5.0GB
            model = Ollama(model="codegemma", temperature=settings["Temperature"])
        elif 'phi' in model_selected.lower():
            # 2.3GB
            model = Ollama(model="phi3", temperature=settings["Temperature"])
        elif 'deepseek-coder' in model_selected.lower():
            # ~800MB
            model = Ollama(model="deepseek-coder", temperature=settings["Temperature"])
        elif 'qwen' in model_selected.lower():
            # ~2.3GB
            model = Ollama(model="qwen", temperature=settings["Temperature"])
        elif 'wizard-math' in model_selected.lower():
            # ~4GB
            model = Ollama(model="wizard-math", temperature=settings["Temperature"])
    elif 'gpt' not in model_selected.lower() and 'groq' in model_selected.lower():
        if 'gemma' in model_selected.lower():
            model = ChatGroq(temperature=settings["Temperature"], model_name='gemma-7b-it')
        elif 'mixtral' in model_selected.lower():
            model = ChatGroq(temperature=settings["Temperature"], model_name='mixtral-8x7b-32768')
        elif 'llama3-8b' in model_selected.lower():
            model = ChatGroq(temperature=settings["Temperature"], model_name='llama3-8b-8192')
        elif 'llama3-70b' in model_selected.lower():
            model = ChatGroq(temperature=settings["Temperature"], model_name='llama3-70b-8192')
        else:
            print("model not found")
    elif 'gpt' in model_selected.lower() and '3.5' in model_selected.lower():
        # https://platform.openai.com/docs/models/overview
        model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=settings["Temperature"])
    elif 'gpt' in model_selected.lower() and '-4' in model_selected.lower():
        model = ChatOpenAI(model="gpt-4-turbo", temperature=settings["Temperature"])
    
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
    
    print("--- The generative content from LLM:\n")
    print(msg.content)

    await msg.send()
