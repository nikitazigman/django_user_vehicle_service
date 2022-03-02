from abc import ABC, abstractmethod

from pydantic import BaseModel

# import requests


class VehicleModelType(BaseModel):
    model: str
    body: str
    year: int
    allowed_actions: list
    allowed_properties: list


class ModelVerificationInt(ABC):
    def __init__(self, vehicle_model: dict) -> None:
        self.vehicle_model = VehicleModelType(**vehicle_model)

    @abstractmethod
    def verify(self) -> tuple:
        """
        Method returns true if model exist in
        vehicle model service otherwise false
        will be returned
        """


class ModelVerification(ModelVerificationInt):
    def verify(self) -> tuple:
        # ToDo: use async request via msg broker to
        # ToDo: vehicle-model and vehicle-properties
        # ToDo: service to verify the model properties
        return (False, {"value": "verification fail"})
