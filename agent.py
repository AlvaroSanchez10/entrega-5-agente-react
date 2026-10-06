import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools import buscar_pedidos


# Carga las variables definidas en el archivo .env
load_dotenv()


# Herramientas disponibles para el agente
tools = [buscar_pedidos]


@lru_cache(maxsize=1)
def get_llm() -> Any:
    """
    Crea el modelo de lenguaje y vincula las herramientas disponibles.

    El modelo se crea únicamente cuando es necesario ejecutarlo.
    La API key se obtiene desde la variable de entorno GROQ_API_KEY.
    """
    llm = ChatGroq(
        model=os.getenv(
            "LLM_MODEL",
            "openai/gpt-oss-20b",
        ),
        temperature=0,
    )

    return llm.bind_tools(tools)


def agent_node(state: MessagesState) -> dict:
    """
    Analiza el estado actual de la conversación.

    El modelo decide autónomamente si necesita utilizar una
    herramienta o si ya cuenta con información suficiente para
    responder al usuario.
    """
    llm_with_tools = get_llm()

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# Creamos el grafo utilizando MessagesState como estado compartido.
builder = StateGraph(MessagesState)


# Nodo encargado del razonamiento del modelo.
builder.add_node(
    "agent",
    agent_node,
)


# Nodo encargado de ejecutar las herramientas solicitadas por el modelo.
builder.add_node(
    "tools",
    ToolNode(tools),
)


# Toda ejecución comienza por el agente.
builder.add_edge(
    START,
    "agent",
)


# Si el modelo solicita una herramienta, tools_condition
# dirige el flujo hacia el nodo "tools".
# Si no solicita herramientas, finaliza la ejecución.
builder.add_conditional_edges(
    "agent",
    tools_condition,
)


# Después de ejecutar una herramienta, volvemos al agente.
# Esto genera el ciclo ReAct:
# Agent -> Tool -> Agent -> ...
builder.add_edge(
    "tools",
    "agent",
)


def create_checkpointer():
    """
    Crea el almacenamiento persistente del estado del agente.

    SqliteSaver permite conservar los mensajes y checkpoints
    asociados a cada thread_id entre distintas ejecuciones.
    """
    return SqliteSaver.from_conn_string(
        "agent_memory.db"
    )