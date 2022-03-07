# from rest_framework import viewsets
from rest_framework import generics, permissions

from .models import Vehicle
from .permissions import IsUserData
from .serializers import VehicleSerializer


class VehicleDetailedView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsUserData, permissions.IsAuthenticated]


class VehicleCreateView(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)


class VehiclesListView(generics.ListAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        self.queryset = Vehicle.objects.filter(
            user_id=self.request.user.id
        )
        return super().get_queryset()
