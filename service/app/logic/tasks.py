from celery import shared_task


@shared_task(
    name="vehicle_model_service.verify_model",
    queue="vehicle_model_service_default",
)
def remote_model_verification(
    model: str, year: int, manufacture: str, body: str
):
    raise NotImplementedError(
        "the function is interface definition for the celery"
    )
