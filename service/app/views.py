# from rest_framework import viewsets
from rest_framework import generics

from .models import Vehicle
from .serializers import VehicleSerializer

# class UserVehicleViewSet(viewsets.ModelViewSet):
#     serializer_class = VehicleSerializer
#     queryset = Vehicle


class VehicleDetailedView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    # filterset_class = UserFilter
    # permission_classes = [IsClient | permissions.IsAuthenticated]


class VehicleCreateView(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


class VehiclesListView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    # filterset_class = UserFilter
