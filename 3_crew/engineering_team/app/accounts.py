class Account:
    def __init__(self, user_id: str, initial_deposit: float) -> None:
        self.user_id = user_id
        self.balance = initial_deposit
        self.portfolio = {}
        self.initial_deposit = initial_deposit
        self.transactions = []

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if self.balance - amount < 0:
            raise ValueError("No se puede retirar, saldo insuficiente.")
        self.balance -= amount

    def buy_shares(self, symbol: str, quantity: int) -> None:
        total_cost = get_share_price(symbol) * quantity
        if total_cost > self.balance:
            raise ValueError("No se puede comprar, saldo insuficiente.")
        self.balance -= total_cost
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity
        self.perform_transaction(f"Compra: {quantity} acciones de {symbol}")

    def sell_shares(self, symbol: str, quantity: int) -> None:
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            raise ValueError("No se puede vender, no posees suficientes acciones.")
        total_revenue = get_share_price(symbol) * quantity
        self.balance += total_revenue
        self.portfolio[symbol] -= quantity
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        self.perform_transaction(f"Venta: {quantity} acciones de {symbol}")

    def get_portfolio_value(self) -> float:
        total_value = sum(
            get_share_price(symbol) * qty for symbol, qty in self.portfolio.items()
        )
        return total_value + self.balance

    def get_profit_loss(self) -> float:
        return self.get_portfolio_value() - self.initial_deposit

    def get_holdings(self) -> dict:
        return self.portfolio

    def get_transactions(self) -> list:
        return self.transactions

    def perform_transaction(self, transaction_detail: str) -> None:
        self.transactions.append(transaction_detail)


def get_share_price(symbol: str) -> float:
    if symbol == "AAPL":
        return 150.00
    elif symbol == "TSLA":
        return 700.00
    elif symbol == "GOOGL":
        return 2800.00
    else:
        raise ValueError("Símbolo de acción no reconocido")
