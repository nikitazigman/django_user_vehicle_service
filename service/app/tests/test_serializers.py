from datetime import date

from app.logic.vehicle_model_verification import MockModelVerification
from app.models import Vehicle
from app.serializers import VehicleSerializer
from django.test import TestCase


# ToDo: complete tests
class UserVehicleSerializersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_vehicle = Vehicle.objects.create(
            user_id=1,
            allowed_actions=[1, 2, 3],
            allowed_properties=[1, 2, 3],
            model="c40",
            manufacture="Volvo",
            body="sedan",
            color="#AAFFCC",
            plate_number="A123AA",
            date=date(day=10, month=10, year=2010),
            vin="1HGBH41JXMN109186",
        )

        cls.data_from_request = {
            "allowed_actions": [1, 2, 3],
            "allowed_properties": [1, 2, 3],
            "model": "c40",
            "manufacture": "Volvo",
            "body": "sedan",
            "color": "#AAF2CC",
            "plate_number": "A123AA",
            "date": date(day=10, month=10, year=2010),
            "vin": "1HGBH41JXMN109185",
        }

        cls.mock_verification_class = MockModelVerification()

    def test_get_user_vehicle(self):
        serializer = VehicleSerializer(instance=self.user_vehicle)
        serializer._verification_class = self.mock_verification_class
        user_vehicle_data = serializer.data

        for key in user_vehicle_data:
            if key == "date":
                self.assertEqual(
                    user_vehicle_data[key],
                    str(self.user_vehicle.__dict__[key]),
                )
                continue

            self.assertEqual(
                user_vehicle_data[key],
                self.user_vehicle.__dict__[key],
            )

    def test_create_user_vehicle(self):
        user_id = 2
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertTrue(serializer.is_valid())
        serializer.save(user_id=user_id)

        self.assertTrue(Vehicle.objects.get(user_id=user_id))

    def test_update_user_vehicle(self):
        update = {"color": "#AFAFAF"}
        serializer = VehicleSerializer(
            self.user_vehicle, data=update, partial=True
        )
        serializer._verification_class = self.mock_verification_class

        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(
            Vehicle.objects.get(id=self.user_vehicle.id).color,
            update["color"],
        )

    def test_vin_regex_validation_length_bigger(self):
        self.data_from_request[
            "vin"
        ] = f"A{self.data_from_request['vin']}"
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_vin_regex_validation_length_smaller(self):
        self.data_from_request["vin"] = self.data_from_request["vin"][
            :-1
        ]
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_vin_regex_validation_small(self):
        self.data_from_request["vin"] = self.data_from_request[
            "vin"
        ].lower()
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_vin_unique_validion(self):
        self.data_from_request["vin"] = self.user_vehicle.vin
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_plate_number_validation_small(self):
        self.data_from_request[
            "plate_number"
        ] = self.data_from_request["plate_number"].lower()
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_color_validation_length_bigger(self):
        self.data_from_request[
            "color"
        ] = f"A{self.data_from_request['color']}"
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_color_validation_length_smaller(self):
        self.data_from_request["color"] = self.data_from_request[
            "color"
        ][:-1]
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_color_validation_small(self):
        self.data_from_request["color"] = self.data_from_request[
            "color"
        ].lower()
        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = self.mock_verification_class
        self.assertFalse(serializer.is_valid())

    def test_vehicle_model_validation(self):
        verification_model = MockModelVerification()
        verification_model.set_verify_resp(False, {"value": "error"})

        serializer = VehicleSerializer(data=self.data_from_request)
        serializer._verification_class = verification_model

        self.assertFalse(serializer.is_valid())
