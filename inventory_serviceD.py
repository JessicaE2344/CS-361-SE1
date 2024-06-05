import zmq
from collections import defaultdict


class InventoryService:
    def __init__(self):
        self.inventory = defaultdict(int)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5558")

    def run(self):
        while True:
            message = self.socket.recv_json()
            if message['type'] == 'update':
                for item in message['items']:
                    self.inventory[item['name']] += item['qty']
                self.socket.send_json({'status': 'inventory_updated'})
                # Print the updated inventory in the terminal
                print("Updated Inventory:")
                for item, qty in self.inventory.items():
                    print(f"{item}: {qty} units available")


if __name__ == "__main__":
    inventory_service = InventoryService()
    inventory_service.run()
