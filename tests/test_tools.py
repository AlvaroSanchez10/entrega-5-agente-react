from tools import buscar_pedidos


def test_buscar_pedidos_cliente_102() -> None:
    result = buscar_pedidos.invoke(
        {"cliente_id": 102}
    )

    assert result["client_id"] == 102
    assert result["name"] == "Ana Martínez"
    assert result["order_count"] == 3
    assert result["total_spent"] == 14500


def test_buscar_pedidos_cliente_205() -> None:
    result = buscar_pedidos.invoke(
        {"cliente_id": 205}
    )

    assert result["client_id"] == 205
    assert result["name"] == "Carlos Gómez"
    assert result["order_count"] == 2
    assert result["total_spent"] == 11000


def test_buscar_pedidos_cliente_inexistente() -> None:
    result = buscar_pedidos.invoke(
        {"cliente_id": 999}
    )

    assert "error" in result
    assert result["error"] == (
        "No se encontró un cliente con ID 999."
    )