class View:
    def get_input(self, prompt):
        return input(prompt)

    def show_message(self, message):
        print(message)

    def show_data(self, data):
        try:
            if not data:
                print("No data available to display.")
                return
            
            for row in data:
                print(row)
        
        except Exception as e:
            print(f"An error occurred while displaying the data: {e}")

    def show_users(self, data):
        """Форматований вивід для таблиці users."""
        for row in data:
            print(f"User ID: {row[0]}\nName: {row[1]}\nPhone Number: {row[2]}\n")

    def show_services(self, data):
        """Форматований вивід для таблиці services."""
        for row in data:
            print(f"Service ID: {row[0]}\nService Name: {row[1]}\nPrice: {row[2]}\n")

    def show_rooms(self, data):
        """Форматований вивід для таблиці rooms."""
        for row in data:
            print(f"Room ID: {row[0]}\nRoom Number: {row[1]}\nRoom Type ID: {row[2]}\n"
                f"User ID: {row[3]}\nCheck-in Date: {row[4]}\nCheck-out Date: {row[5]}\n")

    def show_room_types(self, data):
        """Форматований вивід для таблиці room_type."""
        for row in data:
            print(f"Room Type ID: {row[0]}\nType Name: {row[1]}\nPrice: {row[2]}\n")

    def show_ordering_services(self, data):
        """Форматований вивід для таблиці ordering_services."""
        for row in data:
            print(f"User ID: {row[0]}\nService ID: {row[1]}\nDate: {row[2]}\n")
