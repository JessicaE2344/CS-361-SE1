import zmq


def vending_machine():
    items = {
        1: ("Lays Chips", "Lightly salted and perfect for a quick snack.", 1.50, 0.80, 10),
        2: ("Chocolate Chip Cookies", "Homemade taste in a convenient package.", 1.75, 1.00, 5),
        3: ("Coke", "Refreshing and energizing soft drink.", 2.00, 1.20, 20),
        4: ("Bottled Water", "Clean and pure hydration.", 1.25, 0.50, 15)
    }

    cart = []

    context = zmq.Context()
    receipt_socket = context.socket(zmq.REQ)
    receipt_socket.connect("tcp://localhost:5555")

    profit_socket = context.socket(zmq.REQ)
    profit_socket.connect("tcp://localhost:5556")

    popular_socket = context.socket(zmq.REQ)
    popular_socket.connect("tcp://localhost:5557")

    inventory_socket = context.socket(zmq.REQ)
    inventory_socket.connect("tcp://localhost:5558")

    def show_cart():
        if not cart:
            print("Your cart is currently empty.")
        else:
            print("Items in your cart:")
            total_cost = 0
            for item in cart:
                product, qty = item
                print(f"{product[0]} - ${product[2]:.2f} x {qty}")
                total_cost += product[2] * qty
            print(f"Total cost: ${total_cost:.2f}")

    def checkout():
        if cart:
            show_cart()
            confirm = input("Would you like to proceed to purchase the items in your cart? (yes/no): ")
            if confirm.lower() == 'yes':
                # Send cart data to the receipt microservice
                cart_data = [{"price": item[0][2], "qty": item[1]} for item in cart]
                receipt_socket.send_json(cart_data)

                # Receive total cost from the receipt microservice
                total = receipt_socket.recv_json()
                print(f"Total cost from microservice: ${total:.2f}")

                # Record the sale for profit calculation
                for item in cart:
                    product, qty = item
                    revenue = product[2] * qty
                    cost = product[3] * qty
                    profit_socket.send_json({'type': 'sale', 'revenue': revenue, 'cost': cost})
                    profit_socket.recv_json()  # Acknowledge the sale

                # Record the sale for popular items calculation
                popular_socket.send_json(
                    {'type': 'sale', 'items': [{'name': item[0][0], 'qty': item[1]} for item in cart]})
                popular_socket.recv_json()  # Acknowledge the sale

                # Update inventory locally
                for item in cart:
                    product, qty = item
                    for key, value in items.items():
                        if value[0] == product[0]:
                            items[key] = (value[0], value[1], value[2], value[3], value[4] - qty)

                print("Thank you for your purchase!")
                cart.clear()  # Clear the cart after purchase
            else:
                print("Checkout cancelled.")
        else:
            print("Checkout could not proceed with an empty cart.")

    def check_inventory():
        print("Current inventory status:")
        for key, value in items.items():
            product, description, price, cost, quantity = value
            print(f"{key}: {product}, Price: ${price:.2f}, Cost: ${cost:.2f}, Quantity: {quantity} units available")

    def restock_inventory():
        restock_data = []
        for key, value in items.items():
            product, description, price, cost, quantity = value
            qty = int(input(f"Enter restock quantity for {product}: "))
            restock_data.append({'name': product, 'qty': qty})
            items[key] = (product, description, price, cost, quantity + qty)

        # Send restock data to the inventory microservice
        inventory_socket.send_json({'type': 'update', 'items': restock_data})
        inventory_socket.recv_json()  # Acknowledge the restock
        print("Inventory restocked successfully.")

    print("Welcome to the Vending Machine!")
    print("Are you the owner? Press 9 for inventory check or 8 for restocking.")
    print("Please select a product, or manage your cart:")
    print("1: Lays Chips")
    print("2: Chocolate Chip Cookies")
    print("3: Coke")
    print("4: Bottled Water")
    print("0: Show Cart")
    print("5: Checkout")
    print("6: End of Day Profit Report")
    print("7: Most Popular Items Sold Report")

    while True:
        try:
            choice = int(input("Enter your choice (0, 1-4, 5, 6, 7, 8, or 9 for owners): "))

            if choice == 9:
                check_inventory()
            elif choice == 8:
                restock_inventory()
            elif choice == 0:
                show_cart()
            elif choice == 5:
                checkout()
            elif choice == 6:
                # Request the profit report from the profit microservice
                profit_socket.send_json({'type': 'profit'})
                report = profit_socket.recv_json()
                print(f"Daily Report: Total Revenue: ${report['total_revenue']:.2f}, "
                      f"Total Cost: ${report['total_cost']:.2f}, Profit: ${report['profit']:.2f}")
            elif choice == 7:
                # Request the popular items report from the popular items microservice
                popular_socket.send_json({'type': 'report'})
                report = popular_socket.recv_json()
                print("Most Popular Items Sold Report:")
                for item, qty in report:
                    print(f"{item}: {qty} units sold")
            elif 1 <= choice <= 4:
                product, description, price, cost, _ = items[choice]
                print(f"You selected {product}. Description: {description}. Price: ${price:.2f}")
                proceed = input("Would you like to add this item to your cart? (yes/no): ")
                if proceed.lower() == 'yes':
                    cart.append((items[choice], 1))
                    print("Item added to your cart.")
                else:
                    print("Item not added to your cart.")
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a valid number.")


vending_machine()
