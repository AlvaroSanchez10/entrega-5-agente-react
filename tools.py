from typing import Any

from langchain_core.tools import tool

from database import get_client


@tool
def buscar_pedidos(cliente_id: int) -> dict[str, Any]:
    """
    Busca todos los pedidos realizados por un cliente a partir de su ID.

    Usa esta herramienta cuando necesites conocer los pedidos de un cliente,
    incluyendo cantidad de pedidos, monto total gastado, fechas e identificadores
    de cada pedido. Debes proporcionar el ID numérico del cliente.

    Si el cliente no existe, la herramienta devuelve un mensaje de error indicando
    que no se encontraron datos para ese ID.
    """
    client = get_client(cliente_id)

    if client is None:
        return {
            "error": f"No se encontró un cliente con ID {cliente_id}."
        }

    orders = client["orders"]
    total_spent = sum(order["total"] for order in orders)

    return {
        "client_id": client["client_id"],
        "name": client["name"],
        "order_count": len(orders),
        "total_spent": total_spent,
        "orders": orders,
    }