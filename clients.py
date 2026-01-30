
class Client:
    def __init__(self, cnpj):
        self.cnpj = cnpj
        self.sales = {}
        self.returns = {}
        self.purcharses = {}

    def sum_all(self):
        result = {}

        all_periods = set(self.sales.keys()) | set(self.returns.keys()) | set(self.purcharses.keys())

        for period in all_periods:
            ts = sum(self.sales.get(period, []))
            tr = sum(self.returns.get(period, []))
            tp = sum(self.purcharses.get(period, []))
            base = ts - tr

            result[period] = [ts, tr, tp, base]

        return result
    
    def __eq__(self, other):
        return isinstance(other, Client) and self.cnpj == other.cnpj

    def __repr__(self):
        return f"Client({self.cnpj})"