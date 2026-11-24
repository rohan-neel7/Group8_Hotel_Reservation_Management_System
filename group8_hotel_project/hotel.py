"""Core logic for rooms, customers, reservations, and billing (CO3, CO4, CO5)."""

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional
from uuid import uuid4

from models import (
    Customer,
    DeluxeRoom,
    Reservation,
    Room,
    StandardRoom,
    Suite,
    ValidationError,
)
from storage import JsonStorage, StorageError


class HotelError(Exception):
    """Base exception for hotel application errors."""


class RoomNotFoundError(HotelError):
    pass


class CustomerNotFoundError(HotelError):
    pass


class ReservationNotFoundError(HotelError):
    pass


class RoomUnavailableError(HotelError):
    pass


class HotelService:
    ROOMS_FILE = "rooms.json"
    CUSTOMERS_FILE = "customers.json"
    RESERVATIONS_FILE = "reservations.json"

    def __init__(self, data_directory: str | Path = "data") -> None:
        self.storage = JsonStorage(data_directory)
        self._ensure_initial_rooms()
        # CO3 Data Structures: Dictionaries for fast O(1) lookup by ID or room number
        self.rooms: Dict[int, Room] = self._load_rooms()
        self.customers: Dict[str, Customer] = self._load_customers()
        self.reservations: Dict[str, Reservation] = self._load_reservations()

    def _ensure_initial_rooms(self) -> None:
        path = self.storage.path_for(self.ROOMS_FILE)
        if path.exists():
            return
        sample_rooms = [
            StandardRoom(101, 2000).to_dict(),
            StandardRoom(102, 2200).to_dict(),
            DeluxeRoom(201, 3200, 300).to_dict(),
            DeluxeRoom(202, 3500, 300).to_dict(),
            Suite(301, 5500, 700).to_dict(),
        ]
        self.storage.write_json(self.ROOMS_FILE, sample_rooms)

    def _load_rooms(self) -> Dict[int, Room]:
        records = self.storage.read_json(self.ROOMS_FILE, [])
        if not isinstance(records, list):
            raise StorageError("rooms.json must contain a JSON list.")
        rooms: Dict[int, Room] = {}
        try:
            for record in records:
                room = Room.from_dict(record)
                if room.room_number in rooms:
                    raise ValidationError(f"Duplicate room number: {room.room_number}.")
                rooms[room.room_number] = room
        except (KeyError, TypeError, ValueError) as exc:
            raise StorageError(f"Invalid room record: {exc}") from exc
        return rooms

    def _load_customers(self) -> Dict[str, Customer]:
        records = self.storage.read_json(self.CUSTOMERS_FILE, [])
        if not isinstance(records, list):
            raise StorageError("customers.json must contain a JSON list.")
        customers: Dict[str, Customer] = {}
        try:
            for record in records:
                customer = Customer.from_dict(record)
                customers[customer.customer_id] = customer
        except (KeyError, TypeError, ValueError) as exc:
            raise StorageError(f"Invalid customer record: {exc}") from exc
        return customers

    def _load_reservations(self) -> Dict[str, Reservation]:
        records = self.storage.read_json(self.RESERVATIONS_FILE, [])
        if not isinstance(records, list):
            raise StorageError("reservations.json must contain a JSON list.")
        reservations: Dict[str, Reservation] = {}
        try:
            for record in records:
                reservation = Reservation.from_dict(record)
                reservations[reservation.reservation_id] = reservation
        except (KeyError, TypeError, ValueError) as exc:
            raise StorageError(f"Invalid reservation record: {exc}") from exc
        return reservations

    def _save_customers(self) -> None:
        data = [customer.to_dict() for customer in self.customers.values()]
        self.storage.write_json(self.CUSTOMERS_FILE, data)

    def _save_reservations(self) -> None:
        data = [reservation.to_dict() for reservation in self.reservations.values()]
        self.storage.write_json(self.RESERVATIONS_FILE, data)

    @staticmethod
    def parse_booking_dates(check_in: str, check_out: str) -> tuple[date, date, int]:
        """CO3 Tuple & String operations: clean date strings and return (start, end, nights)."""
        try:
            start = date.fromisoformat(check_in.strip())
            end = date.fromisoformat(check_out.strip())
        except (AttributeError, ValueError) as exc:
            raise ValidationError("Enter valid dates in YYYY-MM-DD format.") from exc

        if start < date.today():
            raise ValidationError("Check-in date cannot be in the past.")
        if end <= start:
            raise ValidationError("Check-out must be after check-in.")
        return start, end, (end - start).days

    def list_rooms(self) -> List[Room]:
        return sorted(self.rooms.values(), key=lambda room: room.room_number)

    def get_room_types(self) -> set[str]:
        """CO3 Set: return unique room categories available in the hotel."""
        return {room.room_type for room in self.rooms.values()}

    def is_room_available(self, room_number: int, check_in: date, check_out: date) -> bool:
        for reservation in self.reservations.values():
            if reservation.room_number != room_number or reservation.status != "CONFIRMED":
                continue
            existing_start = date.fromisoformat(reservation.check_in)
            existing_end = date.fromisoformat(reservation.check_out)
            # Two stays overlap when each begins before the other ends
            if check_in < existing_end and existing_start < check_out:
                return False
        return True

    def search_available_rooms(
        self, room_type_query: str, check_in: str, check_out: str
    ) -> List[Room]:
        """CO3 String Searching: case-insensitive search on room type."""
        start, end, _ = self.parse_booking_dates(check_in, check_out)
        query = room_type_query.strip().lower()
        if not query:
            raise ValidationError("Enter a room type to search for.")

        matches = []
        for room in self.list_rooms():
            if query in room.room_type.lower() and self.is_room_available(room.room_number, start, end):
                matches.append(room)
        return matches

    def register_customer(self, full_name: str, phone: str, email: str = "") -> Customer:
        """CO3 String formatting & validation: normalize customer name, phone, and email."""
        full_name = " ".join(full_name.strip().split()).title()
        phone = phone.strip()
        email = email.strip().lower()

        if len(full_name) < 2:
            raise ValidationError("Customer name must contain at least two characters.")
        if not phone.isdigit() or not (7 <= len(phone) <= 15):
            raise ValidationError("Phone number must contain 7 to 15 digits.")
        if email and ("@" not in email or email.startswith("@") or email.endswith("@")):
            raise ValidationError("Enter a valid email address or leave it blank.")

        customer_id = f"C{uuid4().hex[:8].upper()}"
        customer = Customer(customer_id, full_name, phone, email)
        self.customers[customer_id] = customer
        self._save_customers()
        return customer

    def search_customers(self, name_query: str) -> List[Customer]:
        """CO3 String Searching: case-insensitive substring search on customer names."""
        query = name_query.strip().lower()
        if not query:
            raise ValidationError("Enter a name to search for.")
        matches = [
            customer for customer in self.customers.values()
            if query in customer.full_name.lower()
        ]
        return sorted(matches, key=lambda c: c.full_name.lower())

    def create_reservation(
        self, customer_id: str, room_number: int | str,
        check_in: str, check_out: str
    ) -> Reservation:
        customer_id = customer_id.strip().upper()
        if customer_id not in self.customers:
            raise CustomerNotFoundError("Customer ID was not found. Register the customer first.")

        try:
            number = int(room_number)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Room number must be a valid integer.") from exc
        if number not in self.rooms:
            raise RoomNotFoundError(f"Room {number} does not exist.")

        start, end, nights = self.parse_booking_dates(check_in, check_out)
        if not self.is_room_available(number, start, end):
            raise RoomUnavailableError(
                f"Room {number} is already reserved for some or all of those dates."
            )

        room = self.rooms[number]
        # CO5 Polymorphism: calls calculate_charge() on the specific Room subclass at runtime
        total_charge = room.calculate_charge(nights)
        reservation_id = f"R{uuid4().hex[:8].upper()}"
        reservation = Reservation(
            reservation_id=reservation_id,
            customer_id=customer_id,
            room_number=number,
            check_in=start.isoformat(),
            check_out=end.isoformat(),
            nights=nights,
            total_charge=total_charge,
        )
        self.reservations[reservation_id] = reservation
        self._save_reservations()
        return reservation

    def cancel_reservation(self, reservation_id: str) -> Reservation:
        key = reservation_id.strip().upper()
        reservation = self.reservations.get(key)
        if reservation is None:
            raise ReservationNotFoundError("Reservation ID was not found.")
        if reservation.status == "CANCELLED":
            raise ValidationError("This reservation is already cancelled.")
        reservation.status = "CANCELLED"
        self._save_reservations()
        return reservation

    def list_reservations(self, status: Optional[str] = None) -> List[Reservation]:
        records = list(self.reservations.values())
        if status:
            records = [r for r in records if r.status == status.upper()]
        return sorted(records, key=lambda r: (r.check_in, r.reservation_id))

    def get_customer(self, customer_id: str) -> Customer:
        try:
            return self.customers[customer_id.strip().upper()]
        except KeyError as exc:
            raise CustomerNotFoundError("Customer ID was not found.") from exc

    def get_room(self, room_number: int) -> Room:
        try:
            return self.rooms[int(room_number)]
        except (KeyError, ValueError) as exc:
            raise RoomNotFoundError("Room number was not found.") from exc
