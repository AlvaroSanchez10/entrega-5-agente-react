import json
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).parent / "data" / "orders.json"


def load_database() -> dict[str, Any]:
    """Carga la base de datos ficticia de clientes y pedidos."""
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_client(client_id: int) -> dict[str, Any] | None:
    """Busca un cliente por su identificador."""
    database = load_database()

    for client in database["clients"]:
        if client["client_id"] == client_id:
            return client

    return None