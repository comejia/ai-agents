import gradio as gr
import sys
import os

# Asegura que el módulo accounts.py pueda ser encontrado
# Asume que app.py y accounts.py están en el mismo directorio
sys.path.append(os.path.dirname(__file__))

from accounts import Account, get_share_price

# Instancia global de la cuenta para la demostración de un solo usuario
demo_account = None

# Componentes de salida de Gradio (definidos más tarde en gr.Blocks)
# Se necesitan referencias para usarlos como claves en el diccionario de actualizaciones
balance_output = None
portfolio_output = None
portfolio_value_output = None
profit_loss_output = None
transactions_output = None
status_message_output = None


def get_current_account_status():
    global demo_account

    # Este diccionario se llenará con las actualizaciones para los componentes de Gradio
    status_updates = {}

    if demo_account is None:
        status_updates[balance_output] = "N/A"
        status_updates[portfolio_output] = "No hay posiciones."
        status_updates[portfolio_value_output] = "N/A"
        status_updates[profit_loss_output] = "N/A"
        status_updates[transactions_output] = "No hay transacciones."
        status_updates[status_message_output] = "No hay cuenta creada."
        return status_updates

    try:
        balance = f"${demo_account.balance:.2f}"
        portfolio = demo_account.get_holdings()
        portfolio_str_items = []
        for symbol, qty in portfolio.items():
            try:
                price = get_share_price(symbol)
                portfolio_str_items.append(
                    f"{symbol}: {qty} acciones (precio actual: ${price:.2f})"
                )
            except ValueError:  # Captura si get_share_price falla para un símbolo
                portfolio_str_items.append(
                    f"{symbol}: {qty} acciones (precio desconocido)"
                )
        portfolio_str = (
            "\n".join(portfolio_str_items)
            if portfolio_str_items
            else "No hay posiciones."
        )

        portfolio_value = f"${demo_account.get_portfolio_value():.2f}"
        profit_loss = f"${demo_account.get_profit_loss():.2f}"
        transactions = (
            "\n".join(demo_account.get_transactions())
            if demo_account.get_transactions()
            else "No hay transacciones."
        )

        status_updates[balance_output] = balance
        status_updates[portfolio_output] = portfolio_str
        status_updates[portfolio_value_output] = portfolio_value
        status_updates[profit_loss_output] = profit_loss
        status_updates[transactions_output] = transactions
        status_updates[status_message_output] = (
            ""  # Se sobrescribirá con mensajes específicos de la acción
        )

        return status_updates
    except Exception as e:
        status_updates[balance_output] = "Error"
        status_updates[portfolio_output] = "Error"
        status_updates[portfolio_value_output] = "Error"
        status_updates[profit_loss_output] = "Error"
        status_updates[transactions_output] = "Error"
        status_updates[status_message_output] = (
            f"Error inesperado al obtener el estado: {e}"
        )
        return status_updates


def update_all_outputs_with_message(message: str):
    # Esta función auxiliar obtiene el estado actual y luego añade el mensaje
    status_updates = get_current_account_status()
    status_updates[status_message_output] = message
    return status_updates


def create_account_gradio(user_id_input: str, initial_deposit_input: float):
    global demo_account
    if demo_account is not None:
        return update_all_outputs_with_message(
            "Ya existe una cuenta. Reinicia la aplicación para crear una nueva."
        )

    try:
        if not user_id_input.strip():
            raise ValueError("El ID de usuario no puede estar vacío.")
        if initial_deposit_input < 0:
            raise ValueError("El depósito inicial no puede ser negativo.")

        demo_account = Account(user_id_input, initial_deposit_input)
        return update_all_outputs_with_message(
            f"Cuenta '{user_id_input}' creada exitosamente con un depósito inicial de ${initial_deposit_input:.2f}."
        )
    except Exception as e:
        return update_all_outputs_with_message(f"Error al crear la cuenta: {e}")


def deposit_gradio(amount: float):
    global demo_account
    if demo_account is None:
        return update_all_outputs_with_message("Por favor, crea una cuenta primero.")
    try:
        if amount <= 0:
            raise ValueError("La cantidad a depositar debe ser positiva.")
        demo_account.deposit(amount)
        return update_all_outputs_with_message(
            f"Se depositaron ${amount:.2f} exitosamente."
        )
    except Exception as e:
        return update_all_outputs_with_message(f"Error al depositar: {e}")


def withdraw_gradio(amount: float):
    global demo_account
    if demo_account is None:
        return update_all_outputs_with_message("Por favor, crea una cuenta primero.")
    try:
        if amount <= 0:
            raise ValueError("La cantidad a retirar debe ser positiva.")
        demo_account.withdraw(amount)
        return update_all_outputs_with_message(
            f"Se retiraron ${amount:.2f} exitosamente."
        )
    except ValueError as e:
        return update_all_outputs_with_message(f"Error al retirar: {e}")
    except Exception as e:
        return update_all_outputs_with_message(
            f"Ocurrió un error inesperado al retirar: {e}"
        )


def buy_shares_gradio(symbol: str, quantity: int):
    global demo_account
    if demo_account is None:
        return update_all_outputs_with_message("Por favor, crea una cuenta primero.")
    try:
        if quantity <= 0:
            raise ValueError(
                "La cantidad de acciones debe ser un número entero positivo."
            )
        demo_account.buy_shares(symbol, quantity)
        return update_all_outputs_with_message(
            f"Se compraron {quantity} acciones de {symbol} exitosamente."
        )
    except ValueError as e:
        return update_all_outputs_with_message(f"Error al comprar acciones: {e}")
    except Exception as e:
        return update_all_outputs_with_message(
            f"Ocurrió un error inesperado al comprar: {e}"
        )


def sell_shares_gradio(symbol: str, quantity: int):
    global demo_account
    if demo_account is None:
        return update_all_outputs_with_message("Por favor, crea una cuenta primero.")
    try:
        if quantity <= 0:
            raise ValueError(
                "La cantidad de acciones debe ser un número entero positivo."
            )
        demo_account.sell_shares(symbol, quantity)
        return update_all_outputs_with_message(
            f"Se vendieron {quantity} acciones de {symbol} exitosamente."
        )
    except ValueError as e:
        return update_all_outputs_with_message(f"Error al vender acciones: {e}")
    except Exception as e:
        return update_all_outputs_with_message(
            f"Ocurrió un error inesperado al vender: {e}"
        )


# Interfaz de Gradio
with gr.Blocks(title="Sistema de Gestión de Cuentas de Trading") as demo:
    gr.Markdown("# Plataforma de Simulación de Trading")
    gr.Markdown(
        "Este sistema permite crear una cuenta, gestionar fondos y operar con acciones de forma simulada."
    )

    with gr.Column():
        with gr.Row():
            gr.Markdown("## Estado de la Cuenta")
        with gr.Row():
            balance_output = gr.Textbox(
                label="Saldo Actual", interactive=False, value="N/A"
            )
            portfolio_value_output = gr.Textbox(
                label="Valor Total del Portafolio (incl. efectivo)",
                interactive=False,
                value="N/A",
            )
            profit_loss_output = gr.Textbox(
                label="Ganancia / Pérdida", interactive=False, value="N/A"
            )
        with gr.Row():
            portfolio_output = gr.Textbox(
                label="Posiciones (Holdings)",
                lines=5,
                interactive=False,
                value="No hay posiciones.",
            )
        with gr.Row():
            transactions_output = gr.Textbox(
                label="Historial de Transacciones",
                lines=10,
                interactive=False,
                value="No hay transacciones.",
            )
        with gr.Row():
            status_message_output = gr.Textbox(
                label="Mensajes del Sistema",
                lines=2,
                interactive=False,
                elem_id="status_message_output",
                value="No hay cuenta creada. Por favor, crea una cuenta en la pestaña 'Crear Cuenta'.",
            )

    with gr.Tab("Crear Cuenta"):
        gr.Markdown("### 1. Crear Nueva Cuenta")
        user_id_input = gr.Textbox(
            label="ID de Usuario", value="demo_user", interactive=True
        )
        initial_deposit_input = gr.Number(
            label="Depósito Inicial", value=10000.0, minimum=0
        )
        create_btn = gr.Button("Crear Cuenta")

    with gr.Tab("Depositar/Retirar Fondos"):
        gr.Markdown("### 2. Gestionar Fondos")
        fund_amount_input = gr.Number(
            label="Cantidad", value=100.0, minimum=0.01
        )  # El mínimo puede ser pequeño
        deposit_btn = gr.Button("Depositar")
        withdraw_btn = gr.Button("Retirar")

    with gr.Tab("Comprar/Vender Acciones"):
        gr.Markdown("### 3. Operar Acciones")
        stock_symbol_input = gr.Dropdown(
            label="Símbolo de Acción", choices=["AAPL", "TSLA", "GOOGL"]
        )
        stock_quantity_input = gr.Number(label="Cantidad", value=1, step=1, minimum=1)
        buy_btn = gr.Button("Comprar Acciones")
        sell_btn = gr.Button("Vender Acciones")

    # Los botones de acción actualizan todos los componentes de salida.
    # Usamos la sintaxis de diccionario para actualizar múltiples outputs de Gradio.
    create_btn.click(
        create_account_gradio,
        inputs=[user_id_input, initial_deposit_input],
        outputs=[
            balance_output,
            portfolio_output,
            portfolio_value_output,
            profit_loss_output,
            transactions_output,
            status_message_output,
        ],
    )

    deposit_btn.click(
        deposit_gradio,
        inputs=[fund_amount_input],
        outputs=[
            balance_output,
            portfolio_output,
            portfolio_value_output,
            profit_loss_output,
            transactions_output,
            status_message_output,
        ],
    )

    withdraw_btn.click(
        withdraw_gradio,
        inputs=[fund_amount_input],
        outputs=[
            balance_output,
            portfolio_output,
            portfolio_value_output,
            profit_loss_output,
            transactions_output,
            status_message_output,
        ],
    )

    buy_btn.click(
        buy_shares_gradio,
        inputs=[stock_symbol_input, stock_quantity_input],
        outputs=[
            balance_output,
            portfolio_output,
            portfolio_value_output,
            profit_loss_output,
            transactions_output,
            status_message_output,
        ],
    )

    sell_btn.click(
        sell_shares_gradio,
        inputs=[stock_symbol_input, stock_quantity_input],
        outputs=[
            balance_output,
            portfolio_output,
            portfolio_value_output,
            profit_loss_output,
            transactions_output,
            status_message_output,
        ],
    )

    # Actualizar el estado inicial cuando la aplicación carga
    demo.load(
        get_current_account_status,
        inputs=[],
        outputs=[
            balance_output,
            portfolio_output,
            portfolio_value_output,
            profit_loss_output,
            transactions_output,
            status_message_output,
        ],
    )

demo.launch()
