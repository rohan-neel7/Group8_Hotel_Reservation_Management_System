# Group 8 - Hotel Reservation Management System

A clean, menu-driven Python application that manages hotel rooms, customers, reservations, and billing. Designed for the **Group 8** project brief and optimized for live **Code Walkthrough & Viva (CO3, CO4, CO5)**.

---

## Project Requirements Covered

- Maintain room information and availability (`data/rooms.json`).
- Register customer details with string normalization (`data/customers.json`).
- Search available rooms by room type and date range.
- Create and cancel reservations (`data/reservations.json`).
- Calculate room charges dynamically using polymorphism.
- Handle invalid room numbers, unavailable rooms, invalid dates/input, and file errors with custom exceptions.
- Implement `Room`, `StandardRoom`, `DeluxeRoom`, and `Suite` classes demonstrating inheritance and polymorphism.

---

## How to Run

Requires Python 3.10+ (standard library only, no external packages required).

```bash
cd group8_hotel_project
python main.py
```

### Run Automated Unit Tests

```bash
cd group8_hotel_project
python -m unittest discover -s tests -v
```

---

## Course Outcomes Mapping (Viva & Walkthrough Guide)

### CO3 – Data Structures & String Operations (10 Marks)
1. **Dictionaries (`dict`)**:
   - `self.rooms`, `self.customers`, and `self.reservations` in `HotelService` (`hotel.py`) map unique IDs/room numbers (`101`, `"C1234..."`, `"R5678..."`) to objects for fast $O(1)$ lookup.
2. **Lists (`list`)**:
   - Used in `list_rooms()`, `search_available_rooms()`, `search_customers()`, and JSON list serialization.
3. **Tuples (`tuple`)**:
   - `get_services()` in `models.py` returns an immutable tuple of complimentary room services (`("Wi-Fi", "TV")`, etc.).
   - `parse_booking_dates()` returns `(start_date, end_date, nights)`.
4. **Sets (`set`)**:
   - `get_room_types()` in `hotel.py` uses a set comprehension `{room.room_type for room in self.rooms.values()}` to extract unique room categories.
5. **String Operations**:
   - **Search**: Case-insensitive substring matching using `.strip().lower()` in `search_available_rooms()` and `search_customers()`.
   - **Formatting/Cleaning**: Customer names are normalized with `" ".join(full_name.strip().split()).title()`, emails with `.strip().lower()`, and phone numbers validated with `.isdigit()`.

### CO4 – File Handling & Exception Handling (10 Marks)
1. **JSON Persistence (`storage.py`)**:
   - `JsonStorage.read_json()` and `JsonStorage.write_json()` use context managers (`with path.open(...) as file:`) and `json.load()` / `json.dump()` to store rooms, customers, and reservations inside the `data/` folder.
2. **Exception Handling**:
   - Catches `json.JSONDecodeError` (corrupted JSON file) and `OSError` (file permission/missing directory errors) and wraps them in a custom `StorageError`.
   - Domain-specific custom exceptions: `ValidationError`, `RoomNotFoundError`, `CustomerNotFoundError`, `ReservationNotFoundError`, and `RoomUnavailableError`.
   - `main.py` wraps menu execution in a `try...except` block so invalid inputs never crash the program.

### CO5 – OOP: Classes, Inheritance & Polymorphism (10 Marks)
1. **Class Hierarchy & Inheritance (`models.py`)**:
   - Base class: `Room(room_number, price_per_night, amenities_fee_per_night)`
   - Subclasses inheriting from `Room`: `StandardRoom`, `DeluxeRoom`, and `Suite`.
   - Additional domain classes: `Customer` and `Reservation` with explicit `__init__`, `to_dict()`, and `from_dict()` methods.
2. **Polymorphism (`calculate_charge` & `get_services`)**:
   - `StandardRoom.calculate_charge(nights)`: Base price $\times$ nights.
   - `DeluxeRoom.calculate_charge(nights)`: (Base price + amenities fee) $\times$ nights.
   - `Suite.calculate_charge(nights)`: (Base price + premium amenities fee) $\times$ nights, with a **10% discount for stays of 3 or more nights**.
   - Each subclass also overrides `get_services()` to return room-specific complimentary services.
   - In `HotelService.create_reservation()`, calling `room.calculate_charge(nights)` automatically executes the matching subclass method at runtime without `if/elif` checks on the room type.

---

## Common Live Modification Prompts in Code Walkthrough (15 Marks)

If the examiner asks you to modify the code live during the walkthrough, here are quick examples:

1. **"Change the Suite discount from 3+ nights to 5+ nights"**:
   - Open `models.py` → `Suite.calculate_charge()` → change `if nights >= 3:` to `if nights >= 5:`.
2. **"Add a new room or change room price"**:
   - Edit `data/rooms.json` (or `_ensure_initial_rooms()` in `hotel.py`) and add a room entry.
3. **"Add a 12% GST tax to all room bills"**:
   - In `hotel.py` → `create_reservation()`, multiply `total_charge = round(room.calculate_charge(nights) * 1.12, 2)`.
