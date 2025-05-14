from rest_framework import status
from rest_framework.generics import ListAPIView, UpdateAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Value, CharField, Case, When, BooleanField
from django.db.models.functions import Concat
from django.db.models import Subquery, OuterRef

from utils.mixins import DynamicPermission
from ..models import Vehicle, VehicleRequest, DocumentType
from user.models import DriverDetail
from ..serializers.vehicleSerializers import VehicleImageSerializer, SelectVehicleSerializer, DriverVehiclesListSerializer, VehicleListViewSerializer, AdminVehicleApprovalSerializer, AdminVehicleStatusListSerailzier, VehicleDetailsSerializer, DraftVehicleListViewSerializer, VehicleFrontImageSerializer
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

    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('vehicle_view')]

    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = ['name', 'vehicle_number', 'driver__user__mobile_number']
    filterset_fields = ['status']

    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    serializer_class = AdminVehicleStatusListSerailzier

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        status = self.request.query_params.get('status')
        driver = VehicleRequest.objects.annotate(name=Concat(F('driver__user__first_name'), Value(' '), F('driver__user__last_name'), output_field=CharField()))
        if status:
            driver = driver.filter(status=status)

        if start_date:
            driver = driver.filter(created_at__date=start_date)
        return driver


class DriverVehicleDetailsView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('vehicle_view')]

    serializer_class = VehicleDetailsSerializer

    def get_object(self):
        try:
            return VehicleRequest.objects.get(id=self.kwargs['pk'])
        except VehicleRequest.DoesNotExist:
            return Response({"status" : "error", "message" :"Validation Error", "errors":{"user": "Does not applied as Driver."}}, status=status.HTTP_400_BAD_REQUEST)


class AdminVehicleApprovalView(UpdateAPIView):
    '''
        Approve or reject vehicle verification requests
    '''
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('vehicle_edit')]

    serializer_class = AdminVehicleApprovalSerializer

    def get_object(self):
        try:
            return VehicleRequest.objects.get(id=self.kwargs['pk'])
        except VehicleRequest.DoesNotExist:
            return Response({"status" : "error", "message" :"Validation Error", "errors":{"user": "Does not applied as Driver."}}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        is_approved = request.data.get("is_approved")
        rejection_reason = request.data.get("rejection_reason")
        if is_approved:
            instance.status = 'approved'
            instance.action_by = request.user
            instance.action_at = timezone.now()
            instance.save()

            vehicle = Vehicle.objects.create(driver=instance.driver, vehicle_number=instance.vehicle_number, vehicle_type=instance.vehicle_type, vehicle_chassis_number=instance.vehicle_chassis_number, vehicle_engine_number=instance.vehicle_engine_number)
            vehicle.verification_documents.set(instance.verification_documents.all())
            vehicle.verified_at = timezone.now()
            vehicle.save()

            instance.driver.in_use = vehicle
            instance.driver.save()
            data = {}
            return Response({"status":"success", 'message': 'Vehicle approved'}, status=status.HTTP_200_OK)
        if rejection_reason:
            instance.status = "rejected"
            instance.rejection_reason = rejection_reason
            instance.action_by = request.user
            instance.action_at = timezone.now()
            instance.save()
            return Response({'message': 'Details rejected', 'rejection_reason': rejection_reason }, status=status.HTTP_200_OK)
        return Response({'error': 'Please provide a rejection reason'}, status=status.HTTP_400_BAD_REQUEST)


class VehicleListView(ListAPIView):

    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('vehicle_view')]

    queryset = VehicleRequest.objects.filter(status = 'approved', deleted_at=None).annotate(name=Concat(F('driver__user__first_name'), Value(' '), F('driver__user__last_name'), output_field=CharField()))
    serializer_class = VehicleListViewSerializer

    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = ['vehicle_number', 'name', 'driver__user__mobile_number']
    filterset_fields = ['status']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']


class DraftVehicleListView(ListAPIView):

    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('vehicle_view')]

    vehicleRequest = VehicleRequest.objects.values_list("driver_id", flat=True).distinct()
    queryset = DriverDetail.objects.filter(in_use=None).exclude(id__in=vehicleRequest).annotate(name=Concat(F('user__first_name'), Value(' '), F('user__last_name'), output_field=CharField()))
    serializer_class = DraftVehicleListViewSerializer

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['vehicle_number', 'name', 'driver__user__mobile_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']


class DriverVehiclesListView(ListAPIView):
    '''
        Get all vehicle verification requests
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverVehiclesListSerializer


    def get_queryset(self):
        user = self.request.user
        try:
            driver = DriverDetail.objects.get(user=user)
            vehicle_front_image_subquery = DocumentType.objects.filter(
                vehicle_approve_documents=OuterRef('pk'),
                document_type="vehicle_front_image"
            ).values('id')[:1]

            vehicles = Vehicle.objects.filter(driver=driver.id, deleted_at=None).prefetch_related("verification_documents").annotate(
                selected=Case(When(id=driver.in_use.id, then=True), default=False, output_field=BooleanField()),
                document_type_id=Subquery(vehicle_front_image_subquery)
            )
            # for i in vehicles:
            #     print("id : ", i.id,
            #             ",vehicle_number:", i.vehicle_number,
            #             ",vehicle_type:", i.vehicle_type,
            #             ",selected:", i.selected,
            #             ",vehicle_front_image:", i.image)


        except DriverDetail.DoesNotExist:
            errors = {
                "Driver": "Driver details not found"
            }
            return Response({"status": "error", "message": "Validation Error", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        except Vehicle.DoesNotExist:
            errors = {
                "Vehicle": "Vehicle details not found"
            }
            return Response({"status": "error", "message": "Validation Error", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        return vehicles

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     # for i in queryset:
    #     #     print(i.image)
    #     document_serializer = self.get_serializer(queryset, many=True)
    #     x = VehicleFrontImageSerializer(data = document_serializer.data, many=True)
    #     x.is_valid(raise_exception=True)
    #     # print(x.data, "PRINT SOMETTHING CRAZY")
    #     data = {"data":document_serializer.data}
    #     # print(document_serializer.data)
    #     # for i in document_serializer.data:
    #     #     x = i["image"]
    #     #     c = DocumentType.objects.get(id=x)
    #     #     print(c.document_image)
    #     return Response({
    #         "status": "success",
    #         "message": "Document types fetched successfully",
    #         "data": data
    #     }, status=status.HTTP_200_OK)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        document_serializer = self.get_serializer(queryset, many=True)
        # print(document_serializer.data)
        for i in document_serializer.data:
            document_type_obj = DocumentType.objects.filter(id = i['document_type_id'])
            document_type_serializer = VehicleFrontImageSerializer(document_type_obj, many=True, context={'request': request})
            # import pdb
            # pdb.set_trace()
            i['vehicle_front_image'] = document_type_serializer.data[0]['document_image']
            # print(document_type_serializer.data[0]['document_image'], "qwerty")
        data = {"data":document_serializer.data}
        return Response({
            "status": "success",
            "message": "Document types fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)


class SelectVehicleView(UpdateAPIView):
    '''
        Select vehicle for driver
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = SelectVehicleSerializer

    def get_object(self):
        user = self.request.user
        try:
            driver = DriverDetail.objects.get(user=user)
        except DriverDetail.DoesNotExist:
            errors = {
                "Driver": "Driver details not found"
            }
            return Response({"status": "error", "message": "Validation Error", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        return driver

    def update(self, request, *args, **kwargs):
        driver = self.get_object()
        vehicle_id = request.data.get('vehicle_id')
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            errors = {
                "Vehicle": "Vehicle details not found"
            }
            return Response({"status": "error", "message": "Validation Error", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        driver.in_use = vehicle
        driver.save()
        data = {"driver_first_name": driver.user.first_name,
                "driver_last_name": driver.user.last_name,
                "vehicle_number": vehicle.vehicle_number}
        return Response({"status":"success", "message":"Vehicle Selected Successfully","data":data}, status = status.HTTP_200_OK)


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