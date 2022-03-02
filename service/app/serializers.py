from django.core.validators import RegexValidator
from rest_framework import serializers, validators

from .logic.vehicle_model_verification import (
    ModelVerification,
    ModelVerificationInt,
)
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    _verification_class = ModelVerification

    def _create_vehicle_model_dict(
        self,
        model: str,
        body: str,
        year: int,
        props: list,
        actions: list,
    ) -> dict:
        return {
            "model": model,
            "body": body,
            "date": year,
            "allowed_properties": props,
            "allowed_actions": actions,
        }

    def _update_vehicle_model(self, data: dict) -> dict:
        vehicle_model = self._create_vehicle_model_dict(
            model=self.instance.model,
            body=self.instance.body,
            year=self.instance.date.year,
            props=self.instance.allowed_properties,
            actions=self.instance.allowed_actions,
        )

        if "year" in data:
            data["year"] = data["year"].year

        for key in vehicle_model:
            if key in data:
                vehicle_model[key] = data[key]

        return vehicle_model

    def _create_vehicle_model(self, data: dict) -> dict:
        return self._create_vehicle_model_dict(
            model=data["model"],
            body=data["body"],
            year=data["year"],
            props=data["allowed_properties"],
            actions=data["allowed_actions"],
        )

    def validate(self, data):
        vehicle_model = {}

        if self.instance:  # we are updating model in db
            vehicle_model = self._update_vehicle_model(data)

        else:  # we are creating model in db
            vehicle_model = self._create_vehicle_model(data)

        model_verificator: ModelVerificationInt = (
            self._verification_class(vehicle_model)
        )
        ver_status, ver_resp = model_verificator.verify()

        if not ver_status:
            raise serializers.ValidationError(ver_resp)

        return super(VehicleSerializer, self).validate(data)

    plate_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]*$",
                message="plate_number includes only capital alphanumeric symbols",
                code="invalid_plate_number",
            ),
        ]
    )

    vin = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9]{17,}$",
                message="VIN includes only capital alphanumeric symbols > 17",
                code="invalid_plate_number",
            ),
            validators.UniqueValidator(
                queryset=Vehicle.objects.all()
            ),
        ]
    )

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "model",
            "body",
            "date",
            "color",
            "plate_number",
            "vin",
            "allowed_actions",
            "allowed_properties",
        ]


# class VehiclePropertyModelSerializer(serializers.ModelSerializer):
#     manufacture: serializers.SlugRelatedField = serializers.SlugRelatedField(
#         read_only=True, many=False, slug_field="name"
#     )

#     class Meta:
#         model = VehicleModel
#         fields = ["id", "name", "manufacture"]


# class NeighborVehicleSerializer(serializers.ModelSerializer):
#     model = VehiclePropertyModelSerializer()
#     body = VehicleBodySerializer()

#     class Meta:
#         model = Vehicle
#         fields = [
#             # "id",
#             "model",
#             "body",
#             "year",
#             "color",
#             "plate_number",
#             "vin",
#             "allowed_actions",
#             "allowed_properties",
#         ]
