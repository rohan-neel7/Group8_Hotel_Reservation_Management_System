"""Automated unit tests for the Hotel Reservation Management System."""

import tempfile
import unittest
from datetime import date, timedelta

from hotel import HotelService, RoomNotFoundError, RoomUnavailableError
from models import ValidationError


class HotelServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.service = HotelService(self.temp_directory.name)
        self.customer = self.service.register_customer(
            "  test   customer  ", "9876543210", "TEST@EXAMPLE.COM"
        )
        self.check_in = (date.today() + timedelta(days=10)).isoformat()
        self.check_out = (date.today() + timedelta(days=12)).isoformat()

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_rooms_load_with_expected_subclasses_and_types_set(self) -> None:
        self.assertEqual(self.service.get_room(101).room_type, "Standard")
        self.assertEqual(self.service.get_room(201).room_type, "Deluxe")
        self.assertEqual(self.service.get_room(301).room_type, "Suite")
        self.assertEqual(self.service.get_room_types(), {"Standard", "Deluxe", "Suite"})

    def test_string_normalization_on_customer_registration(self) -> None:
        self.assertEqual(self.customer.full_name, "Test Customer")
        self.assertEqual(self.customer.email, "test@example.com")

    def test_room_search_uses_type_string(self) -> None:
        rooms = self.service.search_available_rooms(
            "del", self.check_in, self.check_out
        )
        self.assertTrue(rooms)
        self.assertTrue(all(room.room_type == "Deluxe" for room in rooms))

    def test_booking_persists_and_calculates_charge(self) -> None:
        reservation = self.service.create_reservation(
            self.customer.customer_id, 101, self.check_in, self.check_out
        )
        self.assertEqual(reservation.nights, 2)
        self.assertEqual(reservation.total_charge, 4000.0)

        reloaded = HotelService(self.temp_directory.name)
        self.assertIn(reservation.reservation_id, reloaded.reservations)

    def test_polymorphic_billing_and_services_across_subclasses(self) -> None:
        standard = self.service.get_room(101)
        deluxe = self.service.get_room(201)
        suite = self.service.get_room(301)

        # 2 nights billing
        self.assertEqual(standard.calculate_charge(2), 4000.0)
        self.assertEqual(deluxe.calculate_charge(2), 7000.0)
        self.assertEqual(suite.calculate_charge(2), 12400.0)

        # 3 nights Suite billing includes 10% long-stay discount: (5500 + 700) * 3 * 0.90 = 16740.0
        self.assertEqual(suite.calculate_charge(3), 16740.0)

        # Polymorphic services tuple
        self.assertIn("TV", standard.get_services())
        self.assertIn("Mini-Bar", deluxe.get_services())
        self.assertIn("Butler Service", suite.get_services())

    def test_invalid_room_number_is_rejected(self) -> None:
        with self.assertRaises(RoomNotFoundError):
            self.service.create_reservation(
                self.customer.customer_id, 999, self.check_in, self.check_out
            )

    def test_overlapping_booking_is_rejected(self) -> None:
        self.service.create_reservation(
            self.customer.customer_id, 101, self.check_in, self.check_out
        )
        with self.assertRaises(RoomUnavailableError):
            self.service.create_reservation(
                self.customer.customer_id, 101, self.check_in, self.check_out
            )

    def test_cancelled_room_becomes_available(self) -> None:
        reservation = self.service.create_reservation(
            self.customer.customer_id, 101, self.check_in, self.check_out
        )
        self.service.cancel_reservation(reservation.reservation_id)
        self.assertTrue(
            self.service.is_room_available(
                101,
                date.fromisoformat(self.check_in),
                date.fromisoformat(self.check_out),
            )
        )

    def test_invalid_date_range_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create_reservation(
                self.customer.customer_id, 101, self.check_out, self.check_in
            )

    def test_customer_search_is_case_insensitive(self) -> None:
        matches = self.service.search_customers("test cus")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].customer_id, self.customer.customer_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
