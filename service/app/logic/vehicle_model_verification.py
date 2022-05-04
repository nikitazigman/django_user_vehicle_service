from abc import ABC, abstractmethod
from typing import Optional, Tuple

from pydantic import BaseModel

from . import tasks


class VehicleModelType(BaseModel):
    model: str
    body: str
    year: int
    manufacture: str
    allowed_actions: list
    allowed_properties: list


class VerificationResponse:
    def __init__(self, response: Tuple) -> None:
        self.status: bool = response[0]
        self.response: dict = response[1]

    def get_error_msg(self):
        if not self.status:
            return self.response

        if not self.response["verification"]:
            return {
                "verification": "Given model is not supported by the service"
            }

    def get_status(self):
        if self.status and self.response["verification"]:
            return True

        return False


class ModelVerificationInt(ABC):
    def __init__(self) -> None:
        self._vehicle_model: Optional[VehicleModelType] = None

    @property
    def vehicle_model(self):
        return self._vehicle_model

    @vehicle_model.setter
    def vehicle_model(self, vehicle_model: dict):
        self._vehicle_model = VehicleModelType(**vehicle_model)

    def check_model(self):
        if self._vehicle_model is None:
            raise KeyError(
                f"{self._vehicle_model=}. You should first provide model data to vehicle_model"
            )

    @abstractmethod
    def verify(self) -> VerificationResponse:
        """
        Method returns true if model exist in
        vehicle model service otherwise false
        will be returned
        """


class ModelVerification(ModelVerificationInt):
    remote_movel_verification_task = tasks.remote_model_verification

    def request_model_service(self, model: VehicleModelType):
        response = self.remote_movel_verification_task.apply_async(
            args=[
                model.model,
                model.year,
                model.manufacture,
                model.body,
            ]
        )
        return response

    def verify(self) -> VerificationResponse:
        # ToDo: use async request to verify vehicle-properties
        self.check_model()
        # mypy does not understand the vehicle_model cannot be None here
        model_async_object = self.request_model_service(self._vehicle_model)  # type: ignore
        return VerificationResponse(model_async_object.get())


class MockModelVerification(ModelVerificationInt):
    """Mock verification request. For a test purpose only"""

    def __init__(self) -> None:
        self.response = VerificationResponse(
            (True, {"verification": True})
        )
        super().__init__()

    def set_verify_resp(self, response_status: bool, value: dict):
        self.response = VerificationResponse((response_status, value))

    def verify(self) -> VerificationResponse:
        self.check_model()
        return self.response
