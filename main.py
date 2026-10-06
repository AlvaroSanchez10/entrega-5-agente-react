import json
from pathlib import Path

from langchain_core.messages import HumanMessage

from agent import builder, create_checkpointer


TRACE_PATH = Path("traces/react_trace.json")
THREAD_ID = "demo-cliente-1"


def serialize_messages(messages: list) -> list[dict]:
    """Convierte los mensajes de LangGraph en datos serializables a JSON."""
    trace = []

    for message in messages:
        item = {
            "type": message.type,
            "content": message.content,
        }

        if getattr(message, "tool_calls", None):
            item["tool_calls"] = message.tool_calls

        if getattr(message, "name", None):
            item["name"] = message.name

        if getattr(message, "tool_call_id", None):
            item["tool_call_id"] = message.tool_call_id

        trace.append(item)

    return trace


def main() -> None:
    config = {
        "configurable": {
            "thread_id": THREAD_ID,
        },
        "recursion_limit": 10,
    }

    with create_checkpointer() as checkpointer:
        graph = builder.compile(
            checkpointer=checkpointer
        )

        # Primera interacción:
        # obliga al agente a consultar dos clientes.
        first_result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Compará los clientes 102 y 205. "
                            "Decime cuántos pedidos hizo cada uno "
                            "y cuál gastó más en total."
                        )
                    )
                ]
            },
            config=config,
        )

        print("\n--- PRIMERA RESPUESTA ---")
        print(first_result["messages"][-1].content)

        # Segunda interacción:
        # usamos EL MISMO thread_id para demostrar persistencia.
        second_result = graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "¿Y cuál fue el último pedido "
                            "del cliente que gastó más?"
                        )
                    )
                ]
            },
            config=config,
        )

        print("\n--- SEGUNDA RESPUESTA ---")
        print(second_result["messages"][-1].content)

        trace_data = {
            "thread_id": THREAD_ID,
            "recursion_limit": 10,
            "description": (
                "Traza real de ejecución del agente ReAct "
                "con tool calling y memoria persistente."
            ),
            "messages": serialize_messages(
                second_result["messages"]
            ),
        }

        TRACE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with TRACE_PATH.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                trace_data,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        print(
            f"\n✓ Traza guardada en {TRACE_PATH}"
        )


if __name__ == "__main__":
    main()