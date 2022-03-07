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
    def __init__(self) -> None:
        self._vehicle_model = None

    @property
    def vehicle_model(self):
        return self._vehicle_model

    @vehicle_model.setter
    def vehicle_model(self, vehicle_model: dict):
        self._vehicle_model = VehicleModelType(**vehicle_model)

    def _check_model(self):
        if self._vehicle_model is None:
            raise KeyError(
                f"{self._vehicle_model=}. You should first provide model data to vehicle_model"
            )

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
        self._check_model()
        return (False, {"value": "verification fail"})


class MockModelVerification(ModelVerificationInt):
    """Mock verification request. For a test purpose only"""

    def __init__(self) -> None:
        self.response_status = True
        self.value = {"value": "success"}
        super().__init__()

    def set_verify_resp(self, response_status: bool, value: dict):
        self.response_status = response_status
        self.value = value

    def verify(self) -> tuple:
        self._check_model()
        return (self.response_status, self.value)
