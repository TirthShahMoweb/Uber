from rest_framework import status
from rest_framework.generics import ListAPIView, DestroyAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

# from user.views.DriverDetailsViews import CanVerifyDriver
from ..models import Vehicle, VehicleRequest
from user.models import DriverDetail
from ..serializers.vehicleSerializers import VehicleImageSerializer, AdminVehicleStatusListSerailzier, VehicleDetailsSerializer
# , DisplayVehicleSerializer, VehicleVerificationPendingSerializer, ResubmissionVehicleSeralizer



class addVehicleView(CreateAPIView):
    '''
        Add vehicle details for verification
    '''

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = VehicleImageSerializer

    def create(self, request):
        data = request.data
        user = request.user
        serializer = self.get_serializer(data=data, context={'user': user})
        if serializer.is_valid():
            data = serializer.save()
            data = {"vehicle_number": data.vehicle_number,
                    "vehicle_type": data.vehicle_type,
                    "vehicle_chassis_number": data.vehicle_chassis_number,
                    "vehicle_engine_number": data.vehicle_engine_number}
            return Response({'status':'success','message': 'Details submitted for verification','data' : data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminVehicleStatusListView(ListAPIView):
    '''
        Get all vehicle verification requests
    '''
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticated, CanVerifyDriver]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]

    search_fields = ['driver__user__first_name', 'driver__user__last_name', 'vehicle_number', 'driver__user__mobile_number']
    filterset_fields = ['status']

    ordering_fields = ['driver__user__first_name', 'created_at']
    ordering = ['-created_at']
    serializer_class = AdminVehicleStatusListSerailzier

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        status = self.request.query_params.get('status')
        driver = VehicleRequest.objects.all()
        if status:
            driver = driver.filter(status=status)

        if start_date:
            driver = driver.filter(created_at__date=start_date)

        return driver



class DriverVehicleDetailsView(RetrieveAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    serializer_class = VehicleDetailsSerializer

    def get_object(self):
        try:
            return VehicleRequest.objects.get(id=self.kwargs['pk'],)
        except VehicleRequest.DoesNotExist:
            return Response({"status" : "error", "message" :"Validation Error", "errors":{"user": "Does not applied as Driver."}}, status=status.HTTP_400_BAD_REQUEST)

# class vehicleverificationRequest(APIView):
#     '''
#         Get all vehicle verification requests
#     '''
#     # authentication_classes = [JWTAuthentication]
#     # permission_classes = [IsAuthenticated, CanVerifyDriver]

#     def post(self, request, pk):
#         try:
#             vehicle = Vehicle.objects.get(pk=pk)
#         except Vehicle.DoesNotExist:
#             return Response({'error': 'Vehicle request not found'}, status=status.HTTP_404_NOT_FOUND)

#         is_approved = request.data.get("is_approved")
#         rejection_reason = request.data.get("rejection_reason")

#         if is_approved:
#             vehicle.status = 'approved'
#             vehicle.save()
#             vehicle.driver.in_use = vehicle
#             vehicle.driver.save()
#             return Response({'message': 'Vehicle approved'}, status=status.HTTP_200_OK)
#         if rejection_reason:
#             vehicle.status = 'rejected'
#             vehicle.rejection_reason = rejection_reason
#             vehicle.save()
#             return Response({'message': 'Details rejected', 'rejection_reason': rejection_reason , 'resubmit_url' : reverse('vehicle-resubmission',  args=[vehicle.id])}, status=status.HTTP_200_OK)
#         return Response({'error': 'Please provide a rejection reason'}, status=status.HTTP_400_BAD_REQUEST)


# class resubmitVehicleView(APIView):
#     '''
#     Resubmit vehicle details for verification
#     '''
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk):

#         try:
#             driver = DriverDetail.objects.get(user=request.user)
#         except DriverDetail.DoesNotExist:
#             return Response({'error': 'Driver details not found'}, status=status.HTTP_404_NOT_FOUND)

#         try:
#             vehicle = Vehicle.objects.get(driver=driver, pk=pk)
#         except Vehicle.DoesNotExist:
#             return Response({'error': 'Vehicle details not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = ResubmissionVehicleSeralizer(vehicle, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             vehicle.status = 'pending'
#             vehicle.save()
#             return Response({"msg":"We will verify your data within 1 day.", "data" :serializer.data}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class VehicleDetailsView(ListAPIView):
#     '''
#     Get vehicle details
#     '''

#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     serializer_class = DisplayVehicleSerializer

#     def get_queryset(self):

#         user = self.request.user
#         try:
#             driver = DriverDetail.objects.get(user=user)
#         except DriverDetail.DoesNotExist:
#             raise DriverDetail.DoesNotExist('Driver details not found')

#         return Vehicle.objects.filter(driver=driver, status='approved', deleted_at=None)

#     def post(self, request):
#         vehicle_id = request.data['vehicle_id']
#         user = request.user
#         try:
#             driver = DriverDetail.objects.get(user=user)
#             vehicle = Vehicle.objects.get(driver=driver, pk=vehicle_id, status='approved')
#             driver.in_use = vehicle
#         except DriverDetail.DoesNotExist:
#             return Response({'error': 'Driver details not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Vehicle.DoesNotExist:
#             return Response({'error': 'Vehicle not found or not approved'}, status=status.HTTP_404_NOT_FOUND)

#         driver.save()
#         return Response({"message":"Vehicle Selected Successfully"})


# class VehicleDestroyView(DestroyAPIView):
#     """
#     Soft delete the Vehicle
#     """
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         try:
#             driver = DriverDetail.objects.get(user=user)
#             return Vehicle.objects.filter(driver=driver, deleted_at=None)
#         except DriverDetail.DoesNotExist:
#             return Vehicle.objects.none()

#     def destroy(self, request, pk):
#         user = request.user

#         try:
#             driver = DriverDetail.objects.get(user=user)
#         except DriverDetail.DoesNotExist:
#             return Response({'error': 'Driver details not found'}, status=status.HTTP_404_NOT_FOUND)

#         vehicle = get_object_or_404(Vehicle, pk=pk, driver=driver)

#         if driver.in_use == vehicle:
#             # driver.in_use = Vehicle.objects.filter(driver = driver).first()
#             driver.in_use = None
#         vehicle.deleted_at = timezone.now()
#         vehicle.save()

#         return Response({"Message": "Vehicle soft deleted successfully."}, status=status.HTTP_200_OK)