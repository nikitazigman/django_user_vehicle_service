from datetime import date
from random import SystemRandom

from app.logic.vehicle_model_verification import MockModelVerification
from app.models import Vehicle
from app.serializers import VehicleSerializer
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

models_list = [
    {
        "year": 1992,
        "manufacture": "Volvo",
        "model": "960",
        "body": "Sedan",
    },
    {
        "year": 1992,
        "manufacture": "Volvo",
        "model": "940",
        "body": "Wagon",
    },
    {
        "year": 1992,
        "manufacture": "Volvo",
        "model": "740",
        "body": "Wagon",
    },
    {
        "year": 1992,
        "manufacture": "Volvo",
        "model": "240",
        "body": "Wagon",
    },
    {
        "year": 1992,
        "manufacture": "Volkswagen",
        "model": "Passat",
        "body": "Sedan",
    },
    {
        "year": 1992,
        "manufacture": "Toyota",
        "model": "Regular Cab",
        "body": "Pickup",
    },
    {
        "year": 1992,
        "manufacture": "Toyota",
        "model": "Previa",
        "body": "Van/Minivan",
    },
    {
        "year": 1992,
        "manufacture": "Toyota",
        "model": "Paseo",
        "body": "Coupe",
    },
    {
        "year": 2005,
        "manufacture": "Chevrolet",
        "model": "Silverado 3500 Crew Cab",
        "body": "Pickup",
    },
    {
        "year": 2005,
        "manufacture": "Chevrolet",
        "model": "Silverado 2500 HD Regular Cab",
        "body": "Pickup",
    },
    {
        "year": 2005,
        "manufacture": "Chevrolet",
        "model": "Silverado 2500 HD Extended Cab",
        "body": "Pickup",
    },
]


# ToDO: Complete
class ViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sys_random = SystemRandom()
        user_vehicle = {
            "allowed_actions": [1, 2, 3],
            "allowed_properties": [1, 2, 3],
            "model": None,
            "manufacture": None,
            "body": None,
            "color": "#AAFFCC",
            "plate_number": "A123AA",
            "date": date.today(),
            "vin": "1HGBH41JXMN10918x",
        }
        cls.users = []
        for i in range(3):
            cls.users.append(
                User.objects.create_user(
                    username=f"user{i}", password="password"
                )
            )

        for i in range(10):
            random_user = sys_random.choice(cls.users)
            picked_model_number = sys_random.choice(
                range(len(models_list))
            )
            random_model = models_list.pop(picked_model_number)

            random_model["date"] = date(
                year=random_model.pop("year"), month=1, day=1
            )
            user_vehicle.update(**random_model)
            user_vehicle["vin"] = f"{user_vehicle['vin'][:-1]}{i}"

            serializer = VehicleSerializer(data=user_vehicle)
            serializer._verification_class = MockModelVerification()
            # ToDo: when run all tests here I have validation error
            serializer.is_valid(raise_exception=True)
            serializer.save(user_id=random_user.id)

    def test_user_gets_only_their_vehicle_list(self):
        user = self.users[0]
        self.assertTrue(
            self.client.login(
                username=user.username, password="password"
            )
        )
        vehicle_list_resp = self.client.get(
            reverse("user-vehicles-list")
        )

        self.assertEqual(vehicle_list_resp.status_code, 200)

        serializer = VehicleSerializer(
            Vehicle.objects.filter(user_id=user.id), many=True
        )
        expected_vehicle_list = serializer.data
        responsed_vehicle_list = vehicle_list_resp.json()

        self.assertEqual(
            expected_vehicle_list, responsed_vehicle_list
        )

    def test_user_can_get_detail_view_of_only_their_vehicles(self):
        user = self.users[0]
        user_vehicle = Vehicle.objects.filter(user_id=user.id).first()
        self.assertTrue(
            self.client.login(
                username=user.username, password="password"
            )
        )

        vehicle_resp = self.client.get(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user_vehicle.id},
            )
        )

        self.assertEqual(vehicle_resp.status_code, 200)

        serializer = VehicleSerializer(
            Vehicle.objects.get(id=user_vehicle.id)
        )
        expected_vehicle = serializer.data
        responsed_vehicle = vehicle_resp.json()

        self.assertEqual(expected_vehicle, responsed_vehicle)

    def test_user_can_create_vehicle(self):
        user = self.users[0]
        # mock the verification function in the serializer class
        verification_model = MockModelVerification()
        verification_model.set_verify_resp(True, {"v": "t"})
        VehicleSerializer._verification_class = verification_model

        serializer = VehicleSerializer(
            Vehicle.objects.filter(user_id=user.id).first()
        )
        user_vehicle = serializer.data
        new_user_vehicle = user_vehicle
        del new_user_vehicle["id"]
        new_user_vehicle["vin"] = f"2{new_user_vehicle['vin'][1:]}"

        self.assertTrue(
            self.client.login(
                username=user.username, password="password"
            )
        )

        response = self.client.post(
            reverse("user-vehicle-create"),
            data=new_user_vehicle,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Vehicle.objects.filter(
                vin=new_user_vehicle["vin"]
            ).exists()
        )

    def test_user_can_delete_vehicle(self):
        user = self.users[2]
        user_vehicle = Vehicle.objects.filter(user_id=user.id).first()
        self.assertTrue(
            self.client.login(
                username=user.username, password="password"
            )
        )

        vehicle_resp = self.client.delete(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user_vehicle.id},
            )
        )

        self.assertEqual(vehicle_resp.status_code, 204)
        self.assertFalse(
            Vehicle.objects.filter(id=user_vehicle.id).exists()
        )

    # ToDo: figure out how to use mock function to mock verification logic
    def test_user_can_update_vehicle(self):
        user = self.users[0]
        user_vehicle = Vehicle.objects.filter(user_id=user.id).first()

        # mock the verification function in the serializer class
        verification_model = MockModelVerification()
        verification_model.set_verify_resp(True, {"v": "t"})
        VehicleSerializer._verification_class = verification_model

        new_color = {"color": "#CCAA22"}

        self.assertTrue(
            self.client.login(
                username=user.username, password="password"
            )
        )

        response = self.client.patch(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user_vehicle.id},
            ),
            data=new_color,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        serializer = VehicleSerializer(
            Vehicle.objects.get(id=user_vehicle.id)
        )
        updated_vehicle = serializer.data

        self.assertEqual(updated_vehicle["color"], new_color["color"])

    def test_one_user_cannot_get_vehicle_from_another_user(self):
        user0_vehicle = Vehicle.objects.filter(
            user_id=self.users[0].id
        ).first()
        user1 = self.users[1]
        self.assertTrue(
            self.client.login(
                username=user1.username, password="password"
            )
        )

        vehicle_resp = self.client.get(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user0_vehicle.id},
            )
        )

        self.assertEqual(vehicle_resp.status_code, 403)
        # ToDo: check error msg containse clear error definition

    def test_one_user_cannot_update_vehicle_of_another_user(self):
        user0_vehicle = Vehicle.objects.filter(
            user_id=self.users[0].id
        ).first()
        user1 = self.users[1]
        self.assertTrue(
            self.client.login(
                username=user1.username, password="password"
            )
        )

        vehicle_resp = self.client.patch(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user0_vehicle.id},
            ),
            data={"color": "#FFAACC"},
            content_type="application/json",
        )

        self.assertEqual(vehicle_resp.status_code, 403)
        # ToDo: check error msg containse clear error definition

    def test_one_user_cannot_delete_vehicle_of_another_user(self):
        user0_vehicle = Vehicle.objects.filter(
            user_id=self.users[0].id
        ).first()
        user1 = self.users[1]
        self.assertTrue(
            self.client.login(
                username=user1.username, password="password"
            )
        )

        vehicle_resp = self.client.delete(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user0_vehicle.id},
            )
        )

        self.assertEqual(vehicle_resp.status_code, 403)
        # ToDo: check error msg containse clear error definition

    def test_cannot_get_vehicle_without_auth(self):
        user = self.users[0]
        user_vehicle = Vehicle.objects.filter(user_id=user.id).first()

        vehicle_resp = self.client.get(
            reverse(
                "user-vehicle-detailed",
                kwargs={"pk": user_vehicle.id},
            )
        )

        self.assertEqual(vehicle_resp.status_code, 401)
