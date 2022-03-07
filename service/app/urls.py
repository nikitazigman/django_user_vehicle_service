from django.urls import path

from .views import (
    VehicleCreateView,
    VehicleDetailedView,
    VehiclesListView,
)

urlpatterns = [
    path(
        "create/",
        VehicleCreateView.as_view(),
        name="user-vehicle-create",
    ),
    path(
        "<int:pk>",
        VehicleDetailedView.as_view(),
        name="user-vehicle-detailed",
    ),
    path(
        "list", VehiclesListView.as_view(), name="user-vehicles-list"
    ),
]
