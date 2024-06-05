import zmq
from collections import defaultdict


class PopularItemsService:
    def __init__(self):
        self.items_sold = defaultdict(int)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5557")

    def run(self):
        while True:
            message = self.socket.recv_json()
            if message['type'] == 'sale':
                for item in message['items']:
                    self.items_sold[item['name']] += item['qty']
                self.socket.send_json({'status': 'sale_recorded'})
            elif message['type'] == 'report':
                report = sorted(self.items_sold.items(), key=lambda x: x[1], reverse=True)
                self.socket.send_json(report)
                # Print the report in the terminal
                print("Most Popular Items Sold Report:")
                for item, qty in report:
                    print(f"{item}: {qty} units sold")


if __name__ == "__main__":
    popular_items_service = PopularItemsService()
    popular_items_service.run()
