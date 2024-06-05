import zmq

def start_receipt_service():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        # Receive request
        message = socket.recv_json()

        # Calculate the total cost
        total = sum(item['price'] * item['qty'] for item in message)

        print("Total spent at vending machine: %.2f" % total)

        # Send reply
        socket.send_json(total)

if __name__ == "__main__":
    start_receipt_service()