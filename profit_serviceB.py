import zmq
import json


class ProfitService:
    def __init__(self):
        self.total_revenue = 0.0
        self.total_cost = 0.0
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5556")

    def run(self):
        while True:
            message = self.socket.recv_json()
            if message['type'] == 'sale':
                self.total_revenue += message['revenue']
                self.total_cost += message['cost']
                self.socket.send_json({'status': 'sale_recorded'})
            elif message['type'] == 'profit':
                profit = self.total_revenue - self.total_cost
                report = {
                    'total_revenue': self.total_revenue,
                    'total_cost': self.total_cost,
                    'profit': profit
                }
                self.socket.send_json(report)
                # Print the report in the terminal
                print(f"Daily Report: Total Revenue: ${report['total_revenue']:.2f}, "
                      f"Total Cost: ${report['total_cost']:.2f}, Profit: ${report['profit']:.2f}")
                # Reset the counters for the next day
                self.total_revenue = 0.0
                self.total_cost = 0.0


if __name__ == "__main__":
    profit_service = ProfitService()
    profit_service.run()
