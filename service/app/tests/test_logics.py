import pydantic
from app.logic.vehicle_model_verification import MockModelVerification
from django.test import TestCase


class VehicleModelVerificationTest(TestCase):
    def setUp(self) -> None:
        self.model_verification = MockModelVerification()

    def test_correct_field_naming(self):
        vehicle_model = {
            "model": "model",
            "body": "body",
            "year": 123,
            "manufacture": "manufacture",
            "allowed_actions": [1, 2, 3, 4],
            "allowed_properties": [1, 2, 3, 4],
        }

        self.model_verification.vehicle_model = vehicle_model

        self.assertEqual(
            vehicle_model,
            self.model_verification.vehicle_model.dict(),
        )

    def test_incorrect_field_naming(self):
        vehicle_model = {
            "Model": "model",
            "body": "body",
            "year": 123,
            "manufacture": "manufacture",
            "allowed_actions": [1, 2, 3, 4],
            "allowed_properties": [1, 2, 3, 4],
        }

        with self.assertRaises(pydantic.ValidationError):
            self.model_verification.vehicle_model = vehicle_model

    def test_incorrect_field_typing(self):
        vehicle_model = {
            "model": "model",
            "body": 123,
            "year": "asd",
            "manufacture": "manufacture",
            "allowed_actions": [1, 2, 3, 4],
            "allowed_properties": [1, 2, 3, 4],
        }

        with self.assertRaises(pydantic.ValidationError):
            self.model_verification.vehicle_model = vehicle_model
