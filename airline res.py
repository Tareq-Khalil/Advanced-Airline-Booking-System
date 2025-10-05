import os
import csv
import uuid
from datetime import datetime

class Reservation:
    def __init__(self, ticket_id, name, seat):
        self.ticket_id = ticket_id
        self.passenger_name = name
        self.seat = seat

class Flight:
    def __init__(self, flight_number, origin, destination, departure_time, rows=5, cols=4):
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.rows = rows
        self.cols = cols
        self.seat_map = self.generate_seat_map()
        self.reservations = []

    def generate_seat_map(self):
        # Seats like A1, A2, B1, ...
        seat_map = {}
        for r in range(self.rows):
            for c in range(1, self.cols + 1):
                seat_id = chr(65 + r) + str(c)
                seat_map[seat_id] = None
        return seat_map

    def available_seats(self):
        return [seat for seat, name in self.seat_map.items() if name is None]

    def display_seats(self):
        print("\nSeat Map (X = Booked, O = Free)")
        for r in range(self.rows):
            row_letter = chr(65 + r)
            for c in range(1, self.cols + 1):
                seat_id = f"{row_letter}{c}"
                mark = 'X' if self.seat_map[seat_id] else 'O'
                print(f"{seat_id}:{mark}", end="  ")
            print()

    def book_seat(self, name, seat):
        if self.seat_map.get(seat) is not None:
            print("❌ Seat already booked.")
            return None
        ticket_id = str(uuid.uuid4())[:8]
        self.seat_map[seat] = name
        res = Reservation(ticket_id, name, seat)
        self.reservations.append(res)
        print(f"✅ Seat {seat} booked for {name}. Ticket ID: {ticket_id}")
        return res

    def cancel_reservation(self, ticket_id):
        for res in self.reservations:
            if res.ticket_id == ticket_id:
                self.seat_map[res.seat] = None
                self.reservations.remove(res)
                print(f"✅ Reservation {ticket_id} cancelled.")
                return True
        print("❌ Ticket ID not found.")
        return False

    def print_summary(self):
        print(f"{self.flight_number:<10} {self.origin:<12} {self.destination:<12} {self.departure_time:<20} {len(self.reservations)}/{len(self.seat_map)} seats booked")

    def serialize(self):
        data = {
            'flight_number': self.flight_number,
            'origin': self.origin,
            'destination': self.destination,
            'departure_time': self.departure_time,
            'reservations': self.reservations,
            'seat_map': self.seat_map
        }
        return data
class AirlineSystem:
    def __init__(self):
        self.flights = []
        self.filename = "flights.csv"

    def run(self):
        self.load_from_file()
        self.main_menu()

    def main_menu(self):
        while True:
            print("\n===== Airline System Main Menu =====")
            print("1. Admin Login")
            print("2. Passenger Access")
            print("3. Exit")
            choice = input("Choose: ")

            if choice == "1":
                self.admin_menu()
            elif choice == "2":
                self.passenger_menu()
            elif choice == "3":
                self.save_to_file()
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")

    # 🔐 Admin Functions
    def admin_menu(self):
        password = input("Enter admin password: ")
        if password != "admin123":
            print("❌ Incorrect password.")
            return

        while True:
            print("\n--- Admin Menu ---")
            print("1. Add Flight")
            print("2. View All Flights")
            print("3. Back to Main Menu")
            choice = input("Choose: ")

            if choice == "1":
                self.add_flight()
            elif choice == "2":
                self.view_all_flights()
            elif choice == "3":
                break
            else:
                print("Invalid option.")

    def add_flight(self):
        fn = input("Flight Number: ")
        origin = input("Origin: ")
        dest = input("Destination: ")
        dt = input("Departure Time (YYYY-MM-DD HH:MM): ")
        try:
            datetime.strptime(dt, "%Y-%m-%d %H:%M")
        except:
            print("❌ Invalid date format.")
            return
        flight = Flight(fn, origin, dest, dt)
        self.flights.append(flight)
        print("✅ Flight added.")

    def view_all_flights(self):
        print("\nFlight List:")
        print(f"{'Flight':<10}{'Origin':<12}{'Destination':<12}{'Departure Time':<20}Booked")
        print("-" * 60)
        for f in self.flights:
            f.print_summary()

    # 🧑 Passenger Functions
    def passenger_menu(self):
        while True:
            print("\n--- Passenger Menu ---")
            print("1. View Flights")
            print("2. Book Seat")
            print("3. Cancel Reservation")
            print("4. Back to Main Menu")
            choice = input("Choose: ")

            if choice == "1":
                self.view_all_flights()
            elif choice == "2":
                self.book_seat_passenger()
            elif choice == "3":
                self.cancel_passenger()
            elif choice == "4":
                break
            else:
                print("Invalid option.")
    def book_seat_passenger(self):
        fn = input("Enter Flight Number: ")
        flight = self.find_flight(fn)
        if not flight:
            print("❌ Flight not found.")
            return
        name = input("Enter your name: ")
        flight.display_seats()
        seat = input("Choose seat (e.g., A1): ").upper()

        if seat not in flight.available_seats():
            print("❌ Seat unavailable.")
            return

        flight.book_seat(name, seat)

    def cancel_passenger(self):
        fn = input("Enter Flight Number: ")
        ticket_id = input("Enter Ticket ID: ")
        flight = self.find_flight(fn)
        if not flight:
            print("❌ Flight not found.")
            return
        flight.cancel_reservation(ticket_id)

    def find_flight(self, fn):
        for f in self.flights:
            if f.flight_number == fn:
                return f
        return None

    def save_to_file(self):
        with open(self.filename, "w", newline="") as f:
            writer = csv.writer(f)
            for fl in self.flights:
                row = [
                    fl.flight_number,
                    fl.origin,
                    fl.destination,
                    fl.departure_time,
                    fl.rows,
                    fl.cols,
                ]
                writer.writerow(["#FLIGHT"] + row)
                for r in fl.reservations:
                    writer.writerow(["#RES", r.ticket_id, r.passenger_name, r.seat])
        print("📁 Data saved.")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return
        current_flight = None
        with open(self.filename, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                if row[0] == "#FLIGHT":
                    fn, origin, dest, dt, rows, cols = row[1:]
                    current_flight = Flight(fn, origin, dest, dt, int(rows), int(cols))
                    self.flights.append(current_flight)
                elif row[0] == "#RES" and current_flight:
                    tid, name, seat = row[1:]
                    current_flight.seat_map[seat] = name
                    current_flight.reservations.append(Reservation(tid, name, seat))

# 🔥 Main entry point
if __name__ == "__main__":
    system = AirlineSystem()
    system.run()

