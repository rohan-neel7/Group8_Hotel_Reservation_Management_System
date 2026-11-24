"""Domain models for the Hotel Reservation Management System (CO5: OOP)."""


class ValidationError(ValueError):
    """Raised when input or file data is invalid."""


class Room:
    """Base Room class. Subclasses demonstrate inheritance and polymorphism."""

    room_type = "Room"

    def __init__(self, room_number: int, price_per_night: float,
                 amenities_fee_per_night: float = 0.0) -> None:
        if int(room_number) <= 0:
            raise ValidationError("Room number must be a positive integer.")
        if float(price_per_night) <= 0:
            raise ValidationError("Price per night must be greater than zero.")
        if float(amenities_fee_per_night) < 0:
            raise ValidationError("Amenities fee cannot be negative.")

        self.room_number = int(room_number)
        self.price_per_night = float(price_per_night)
        self.amenities_fee_per_night = float(amenities_fee_per_night)

    def calculate_charge(self, nights: int) -> float:
        """Default billing behavior for a generic room."""
        if nights <= 0:
            raise ValidationError("Number of nights must be greater than zero.")
        return round(self.price_per_night * nights, 2)

    def get_services(self) -> tuple[str, ...]:
        """Return a tuple of complimentary services included with the room."""
        return ("Wi-Fi",)

    def to_dict(self) -> dict:
        return {
            "room_number": self.room_number,
            "room_type": self.room_type,
            "price_per_night": self.price_per_night,
            "amenities_fee_per_night": self.amenities_fee_per_night,
        }

    @staticmethod
    def from_dict(data: dict) -> "Room":
        room_classes = {
            "Standard": StandardRoom,
            "Deluxe": DeluxeRoom,
            "Suite": Suite,
        }
        room_type = str(data.get("room_type", "")).strip()
        room_class = room_classes.get(room_type)
        if room_class is None:
            raise ValidationError(f"Unknown room type in data file: {room_type!r}.")
        return room_class(
            room_number=int(data["room_number"]),
            price_per_night=float(data["price_per_night"]),
            amenities_fee_per_night=float(data.get("amenities_fee_per_night", 0.0)),
        )


class StandardRoom(Room):
    """Standard rooms charge only the base nightly rate."""

    room_type = "Standard"

    def calculate_charge(self, nights: int) -> float:
        if nights <= 0:
            raise ValidationError("Number of nights must be greater than zero.")
        return round(self.price_per_night * nights, 2)

    def get_services(self) -> tuple[str, ...]:
        return ("Wi-Fi", "TV")


class DeluxeRoom(Room):
    """Deluxe rooms add a per-night amenities fee to the base rate."""

    room_type = "Deluxe"

    def calculate_charge(self, nights: int) -> float:
        if nights <= 0:
            raise ValidationError("Number of nights must be greater than zero.")
        nightly_total = self.price_per_night + self.amenities_fee_per_night
        return round(nightly_total * nights, 2)

    def get_services(self) -> tuple[str, ...]:
        return ("Wi-Fi", "Breakfast", "Mini-Bar")


class Suite(Room):
    """Suites add a premium amenities fee; stays of 3+ nights get a 10% discount."""

    room_type = "Suite"

    def calculate_charge(self, nights: int) -> float:
        if nights <= 0:
            raise ValidationError("Number of nights must be greater than zero.")
        nightly_total = self.price_per_night + self.amenities_fee_per_night
        total = nightly_total * nights
        if nights >= 3:
            total *= 0.90  # 10% long-stay discount for Suite
        return round(total, 2)

    def get_services(self) -> tuple[str, ...]:
        return ("Wi-Fi", "Breakfast", "Airport Lounge", "Butler Service")


class Customer:
    """Represents a registered hotel guest."""

    def __init__(self, customer_id: str, full_name: str, phone: str, email: str = "") -> None:
        self.customer_id = customer_id
        self.full_name = full_name
        self.phone = phone
        self.email = email

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
        }

    @staticmethod
    def from_dict(data: dict) -> "Customer":
        return Customer(
            customer_id=str(data["customer_id"]),
            full_name=str(data["full_name"]),
            phone=str(data["phone"]),
            email=str(data.get("email", "")),
        )


class Reservation:
    """Represents a room booking and calculated bill."""

    def __init__(self, reservation_id: str, customer_id: str, room_number: int,
                 check_in: str, check_out: str, nights: int,
                 total_charge: float, status: str = "CONFIRMED") -> None:
        self.reservation_id = reservation_id
        self.customer_id = customer_id
        self.room_number = int(room_number)
        self.check_in = check_in
        self.check_out = check_out
        self.nights = int(nights)
        self.total_charge = float(total_charge)
        self.status = status

    def to_dict(self) -> dict:
        return {
            "reservation_id": self.reservation_id,
            "customer_id": self.customer_id,
            "room_number": self.room_number,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "nights": self.nights,
            "total_charge": self.total_charge,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data: dict) -> "Reservation":
        return Reservation(
            reservation_id=str(data["reservation_id"]),
            customer_id=str(data["customer_id"]),
            room_number=int(data["room_number"]),
            check_in=str(data["check_in"]),
            check_out=str(data["check_out"]),
            nights=int(data["nights"]),
            total_charge=float(data["total_charge"]),
            status=str(data.get("status", "CONFIRMED")),
        )
