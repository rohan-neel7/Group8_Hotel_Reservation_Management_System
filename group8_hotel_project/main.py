"""Command-line interface for the Hotel Reservation Management System."""

from pathlib import Path

from hotel import HotelError, HotelService
from models import ValidationError
from storage import StorageError


DATA_DIRECTORY = Path(__file__).parent / "data"


def print_line() -> None:
    print("-" * 78)


def show_rooms(service: HotelService) -> None:
    types_str = ", ".join(sorted(service.get_room_types()))
    print(f"\nROOM DIRECTORY (Categories: {types_str})")
    print_line()
    print(f"{'Room No.':<10}{'Type':<12}{'Base/night':>12}{'Amenities':>12}  {'Included Services'}")
    print_line()
    for room in service.list_rooms():
        services = ", ".join(room.get_services())
        print(
            f"{room.room_number:<10}{room.room_type:<12}"
            f"{room.price_per_night:>12.2f}{room.amenities_fee_per_night:>12.2f}  {services}"
        )
    print_line()
    print("Note: Charges are in INR (₹). Suites receive a 10% discount for 3+ nights.")


def search_rooms(service: HotelService) -> None:
    room_type = input("Room type (Standard / Deluxe / Suite): ")
    check_in = input("Check-in date (YYYY-MM-DD): ")
    check_out = input("Check-out date (YYYY-MM-DD): ")
    rooms = service.search_available_rooms(room_type, check_in, check_out)
    if not rooms:
        print("No rooms of that type are available for those dates.")
        return
    print("\nAvailable rooms:")
    for room in rooms:
        services = ", ".join(room.get_services())
        print(
            f"Room {room.room_number} | {room.room_type} | "
            f"Base: ₹{room.price_per_night:.2f}/night | "
            f"Amenities: ₹{room.amenities_fee_per_night:.2f}/night | "
            f"Services: {services}"
        )


def register_customer(service: HotelService) -> None:
    print("\nCUSTOMER REGISTRATION")
    name = input("Full name: ")
    phone = input("Phone number (digits only): ")
    email = input("Email (optional): ")
    customer = service.register_customer(name, phone, email)
    print(f"Customer registered: {customer.full_name} | Customer ID: {customer.customer_id}")


def create_booking(service: HotelService) -> None:
    print("\nCREATE RESERVATION")
    customer_id = input("Customer ID: ")
    room_number = input("Room number: ")
    check_in = input("Check-in date (YYYY-MM-DD): ")
    check_out = input("Check-out date (YYYY-MM-DD): ")
    reservation = service.create_reservation(
        customer_id, room_number, check_in, check_out
    )
    room = service.get_room(reservation.room_number)
    print("\nRESERVATION CONFIRMED")
    print_line()
    print(f"Reservation ID : {reservation.reservation_id}")
    print(f"Customer ID    : {reservation.customer_id}")
    print(f"Room           : {room.room_number} ({room.room_type})")
    print(f"Services       : {', '.join(room.get_services())}")
    print(f"Stay           : {reservation.check_in} to {reservation.check_out}")
    print(f"Nights         : {reservation.nights}")
    print(f"Total charge   : ₹{reservation.total_charge:,.2f}")
    print_line()


def cancel_booking(service: HotelService) -> None:
    reservation_id = input("Reservation ID to cancel: ")
    reservation = service.cancel_reservation(reservation_id)
    print(f"Reservation {reservation.reservation_id} has been cancelled.")


def show_reservations(service: HotelService) -> None:
    reservations = service.list_reservations()
    if not reservations:
        print("No reservations have been recorded.")
        return
    print("\nRESERVATION RECORDS")
    print_line()
    for reservation in reservations:
        customer = service.get_customer(reservation.customer_id)
        room = service.get_room(reservation.room_number)
        print(f"ID: {reservation.reservation_id} | Status: {reservation.status}")
        print(f"Customer: {customer.full_name} ({customer.customer_id})")
        print(f"Room: {room.room_number} - {room.room_type}")
        print(
            f"Dates: {reservation.check_in} to {reservation.check_out} | "
            f"Nights: {reservation.nights} | "
            f"Total: ₹{reservation.total_charge:,.2f}"
        )
        print_line()


def search_customer(service: HotelService) -> None:
    query = input("Enter all or part of the customer's name: ")
    customers = service.search_customers(query)
    if not customers:
        print("No matching customers found.")
        return
    for customer in customers:
        print(
            f"{customer.customer_id} | {customer.full_name} | "
            f"{customer.phone} | {customer.email or 'No email'}"
        )


def main() -> None:
    try:
        service = HotelService(DATA_DIRECTORY)
    except (StorageError, ValidationError) as exc:
        print(f"Could not start the application: {exc}")
        return

    while True:
        print("\n" + "=" * 78)
        print("                HOTEL RESERVATION MANAGEMENT SYSTEM")
        print("=" * 78)
        print("1. View all rooms")
        print("2. Search available rooms")
        print("3. Register customer")
        print("4. Create reservation")
        print("5. Cancel reservation")
        print("6. View reservations")
        print("7. Search customers")
        print("8. Exit")
        choice = input("Select an option (1-8): ").strip()

        try:
            if choice == "1":
                show_rooms(service)
            elif choice == "2":
                search_rooms(service)
            elif choice == "3":
                register_customer(service)
            elif choice == "4":
                create_booking(service)
            elif choice == "5":
                cancel_booking(service)
            elif choice == "6":
                show_reservations(service)
            elif choice == "7":
                search_customer(service)
            elif choice == "8":
                print("Thank you. Application closed.")
                break
            else:
                print("Invalid menu choice. Enter a number from 1 to 8.")
        except (HotelError, ValidationError, StorageError) as exc:
            print(f"Error: {exc}")
        except (ValueError, TypeError) as exc:
            print(f"Invalid input: {exc}")
        except KeyboardInterrupt:
            print("\nOperation interrupted. Returning to the main menu.")


if __name__ == "__main__":
    main()
