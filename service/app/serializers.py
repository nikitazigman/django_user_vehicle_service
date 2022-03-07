from django.core.validators import RegexValidator
from rest_framework import serializers, validators

from .logic.vehicle_model_verification import ModelVerification
from .models import Vehicle


# ToDo: add regex validator for the color field
# ToDo: forbide an updating the id field
class VehicleSerializer(serializers.ModelSerializer):
    _verification_class = ModelVerification()

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
            "year": year,
            "allowed_properties": props,
            "allowed_actions": actions,
        }

    def _update_vehicle_model(self, data: dict) -> dict:
        if not isinstance(self.instance, Vehicle):
            raise TypeError(
                "instance is not an instance of Vehicle object"
            )

        user_vehicle: Vehicle = self.instance

        vehicle_model = self._create_vehicle_model_dict(
            model=user_vehicle.model,
            body=user_vehicle.body,
            year=user_vehicle.date.year,
            props=user_vehicle.allowed_properties,
            actions=user_vehicle.allowed_actions,
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
            year=data["date"].year,
            props=data["allowed_properties"],
            actions=data["allowed_actions"],
        )

    def validate(self, data):
        vehicle_model = {}

        if self.instance:  # we are updating model in db
            vehicle_model = self._update_vehicle_model(data)

        else:  # we are creating model in db
            vehicle_model = self._create_vehicle_model(data)

        self._verification_class.vehicle_model = vehicle_model

        ver_status, ver_resp = self._verification_class.verify()

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
                regex=r"^[A-Z0-9]{17}$",
                message="VIN includes only capital alphanumeric symbols > 17",
                code="invalid_plate_number",
            ),
            validators.UniqueValidator(
                queryset=Vehicle.objects.all()
            ),
        ]
    )

    color = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"\B(\#+[A-Z0-9]{6})$",
                message="Color should starts with '#' and after have only 6 capital letters or numbers",
                code="invalid_plate_number",
            )
        ]
    )

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "model",
            "manufacture",
            "body",
            "date",
            "color",
            "plate_number",
            "vin",
            "allowed_actions",
            "allowed_properties",
        ]
        read_only_fields = ["id"]
