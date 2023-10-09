class URL:
    def __init__(self):
        self.base_url = "https://rahavard365.com/"

    def stock(self):
        return f"{self.base_url}stock"

    def balance_sheet(self, symbol_id):
        return f"{self.base_url}asset/{symbol_id}/balancesheet"

    def income_statements(self, symbol_id):
        return f"{self.base_url}/asset/{symbol_id}/profitloss"

    def cash_flow(self, symbol_id):
        return f"{self.base_url}/asset/{symbol_id}/cashflow"
