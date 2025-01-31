
class Instance:
    def __init__(self):
        # self.name = name
        self.symbol = None
        self.active_orders = []

    def get_symbol(self):
        return self.symbol
    
    def set_symbol(self, symbol):
        self.symbol = symbol
    
    def get_active_orders(self):
        return self.active_orders
    
    def add_active_order(self, order):
        self.active_orders.append(order)