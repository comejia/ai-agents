from unittest.mock import patch
from accounts import Account, get_share_price
import unittest


class TestAccount(unittest.TestCase):
    def setUp(self):
        # Set up a fresh account for each test
        self.account = Account("user123", 1000.00)

    def test_initialization(self):
        self.assertEqual(self.account.user_id, "user123")
        self.assertEqual(self.account.balance, 1000.00)
        self.assertEqual(self.account.initial_deposit, 1000.00)
        self.assertEqual(self.account.portfolio, {})
        self.assertEqual(self.account.transactions, [])

    def test_deposit(self):
        self.account.deposit(500.00)
        self.assertEqual(self.account.balance, 1500.00)
        self.account.deposit(0.01)
        self.assertEqual(self.account.balance, 1500.01)

    def test_withdraw_sufficient_funds(self):
        self.account.withdraw(200.00)
        self.assertEqual(self.account.balance, 800.00)
        self.account.withdraw(800.00)
        self.assertEqual(self.account.balance, 0.00)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaisesRegex(
            ValueError, "No se puede retirar, saldo insuficiente."
        ):
            self.account.withdraw(1500.00)
        self.assertEqual(
            self.account.balance, 1000.00
        )  # Balance should remain unchanged

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_buy_shares_new_symbol(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 2)  # Cost: 2 * 150 = 300
        self.assertEqual(self.account.balance, 700.00)
        self.assertEqual(self.account.portfolio, {"AAPL": 2})
        self.assertIn("Compra: 2 acciones de AAPL", self.account.transactions)

        self.account.buy_shares("TSLA", 1)  # Cost: 1 * 700 = 700
        self.assertEqual(self.account.balance, 0.00)
        self.assertEqual(self.account.portfolio, {"AAPL": 2, "TSLA": 1})
        self.assertIn("Compra: 1 acciones de TSLA", self.account.transactions)

    @patch("accounts.get_share_price", side_effect=lambda s: {"AAPL": 150.00}.get(s))
    def test_buy_shares_existing_symbol(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 2)  # Initial: 2 shares
        self.account.buy_shares(
            "AAPL", 3
        )  # Add 3 more shares. Cost: 3 * 150 = 450. Current balance: 700 - 450 = 250
        self.assertEqual(self.account.balance, 250.00)
        self.assertEqual(self.account.portfolio, {"AAPL": 5})
        self.assertIn("Compra: 3 acciones de AAPL", self.account.transactions)

    @patch("accounts.get_share_price", side_effect=lambda s: {"AAPL": 150.00}.get(s))
    def test_buy_shares_insufficient_funds(self, mock_get_share_price):
        with self.assertRaisesRegex(
            ValueError, "No se puede comprar, saldo insuficiente."
        ):
            self.account.buy_shares(
                "AAPL", 7
            )  # Cost: 7 * 150 = 1050. Current balance: 1000
        self.assertEqual(self.account.balance, 1000.00)  # Balance unchanged
        self.assertEqual(self.account.portfolio, {})  # Portfolio unchanged
        self.assertEqual(len(self.account.transactions), 0)  # No transaction logged

    @patch("accounts.get_share_price")  # Mock get_share_price to control its behavior
    def test_buy_shares_unrecognized_symbol(self, mock_get_share_price):
        # Configure the mock to raise ValueError, mimicking the real get_share_price
        mock_get_share_price.side_effect = ValueError("Símbolo de acción no reconocido")
        with self.assertRaisesRegex(ValueError, "Símbolo de acción no reconocido"):
            self.account.buy_shares("UNKNOWN", 1)
        self.assertEqual(self.account.balance, 1000.00)
        self.assertEqual(self.account.portfolio, {})

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_sell_shares_partial(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 5)  # Buy 5 AAPL shares (cost 750, balance 250)
        self.account.sell_shares(
            "AAPL", 2
        )  # Sell 2 AAPL shares (revenue 300, balance 550)
        self.assertEqual(self.account.balance, 550.00)
        self.assertEqual(self.account.portfolio, {"AAPL": 3})
        self.assertIn("Venta: 2 acciones de AAPL", self.account.transactions)

    @patch("accounts.get_share_price", side_effect=lambda s: {"AAPL": 150.00}.get(s))
    def test_sell_shares_all(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 3)  # Buy 3 AAPL shares (cost 450, balance 550)
        self.account.sell_shares(
            "AAPL", 3
        )  # Sell all 3 AAPL shares (revenue 450, balance 1000)
        self.assertEqual(self.account.balance, 1000.00)
        self.assertEqual(
            self.account.portfolio, {}
        )  # Portfolio should be empty for AAPL
        self.assertIn("Venta: 3 acciones de AAPL", self.account.transactions)

    def test_sell_shares_not_owned(self):
        with self.assertRaisesRegex(
            ValueError, "No se puede vender, no posees suficientes acciones."
        ):
            self.account.sell_shares("GOOGL", 1)
        self.assertEqual(self.account.balance, 1000.00)
        self.assertEqual(self.account.portfolio, {})

    @patch("accounts.get_share_price", side_effect=lambda s: {"AAPL": 150.00}.get(s))
    def test_sell_shares_more_than_owned(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 2)  # Buy 2 AAPL shares
        with self.assertRaisesRegex(
            ValueError, "No se puede vender, no posees suficientes acciones."
        ):
            self.account.sell_shares("AAPL", 3)  # Try to sell 3
        self.assertEqual(
            self.account.balance, 1000.00 - (2 * 150)
        )  # Balance should be what it was after purchase
        self.assertEqual(
            self.account.portfolio, {"AAPL": 2}
        )  # Portfolio should be unchanged
        self.assertEqual(
            len(self.account.transactions), 1
        )  # Only buy transaction logged

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_get_portfolio_value_empty(self, mock_get_share_price):
        # Initial balance 1000, empty portfolio
        self.assertEqual(self.account.get_portfolio_value(), 1000.00)

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_get_portfolio_value_with_holdings(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 2)  # Balance 700, Portfolio {'AAPL': 2}
        self.account.buy_shares(
            "TSLA", 1
        )  # Balance 0, Portfolio {'AAPL': 2, 'TSLA': 1}
        # Portfolio value: (2 * 150) + (1 * 700) = 300 + 700 = 1000
        # Total value: 1000 (portfolio) + 0 (balance) = 1000
        self.assertEqual(self.account.get_portfolio_value(), 1000.00)

        self.account.deposit(500)  # Balance 500
        # Total value: 1000 (portfolio) + 500 (balance) = 1500
        self.assertEqual(self.account.get_portfolio_value(), 1500.00)

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_get_profit_loss_no_activity(self, mock_get_share_price):
        # Initial deposit 1000.00, current value 1000.00
        self.assertEqual(self.account.get_profit_loss(), 0.00)

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_get_profit_loss_with_profit(self, mock_get_share_price):
        self.account.buy_shares(
            "AAPL", 2
        )  # Cost 300, balance 700, portfolio {'AAPL': 2}
        # Simulate price increase for profit calculation
        mock_get_share_price.side_effect = lambda s: {
            "AAPL": 200.00,
            "TSLA": 700.00,
        }.get(s)
        # Current portfolio value: (2 * 200) + 700 (balance) = 400 + 700 = 1100
        # Profit/Loss: 1100 (current value) - 1000 (initial deposit) = 100
        self.assertEqual(self.account.get_portfolio_value(), 1100.00)
        self.assertEqual(self.account.get_profit_loss(), 100.00)

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_get_profit_loss_with_loss(self, mock_get_share_price):
        self.account.buy_shares(
            "AAPL", 2
        )  # Cost 300, balance 700, portfolio {'AAPL': 2}
        # Simulate price decrease for loss calculation
        mock_get_share_price.side_effect = lambda s: {
            "AAPL": 100.00,
            "TSLA": 700.00,
        }.get(s)
        # Current portfolio value: (2 * 100) + 700 (balance) = 200 + 700 = 900
        # Profit/Loss: 900 (current value) - 1000 (initial deposit) = -100
        self.assertEqual(self.account.get_portfolio_value(), 900.00)
        self.assertEqual(self.account.get_profit_loss(), -100.00)

    @patch("accounts.get_share_price", side_effect=lambda s: {"AAPL": 150.00}.get(s))
    def test_get_holdings(self, mock_get_share_price):
        self.account.buy_shares("AAPL", 2)
        self.assertEqual(self.account.get_holdings(), {"AAPL": 2})
        self.account.withdraw(100)  # Should not affect holdings
        self.assertEqual(self.account.get_holdings(), {"AAPL": 2})

    @patch(
        "accounts.get_share_price",
        side_effect=lambda s: {"AAPL": 150.00, "TSLA": 700.00}.get(s),
    )
    def test_get_transactions(self, mock_get_share_price):
        self.assertEqual(self.account.get_transactions(), [])
        self.account.buy_shares("AAPL", 1)
        self.account.deposit(200)  # deposit is not logged by perform_transaction
        self.account.sell_shares("AAPL", 1)
        expected_transactions = [
            "Compra: 1 acciones de AAPL",
            "Venta: 1 acciones de AAPL",
        ]
        self.assertEqual(self.account.get_transactions(), expected_transactions)


class TestGetSharePrice(unittest.TestCase):
    def test_get_share_price_known_symbols(self):
        self.assertEqual(get_share_price("AAPL"), 150.00)
        self.assertEqual(get_share_price("TSLA"), 700.00)
        self.assertEqual(get_share_price("GOOGL"), 2800.00)

    def test_get_share_price_unknown_symbol(self):
        with self.assertRaisesRegex(ValueError, "Símbolo de acción no reconocido"):
            get_share_price("MSFT")
        with self.assertRaisesRegex(ValueError, "Símbolo de acción no reconocido"):
            get_share_price("INVALID")


if __name__ == "__main__":
    unittest.main()
