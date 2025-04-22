from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from django.db.models import F, Value
from django.db.models.functions import Concat
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..models import DriverDetail, DocumentType, User, DriverRequest, RolePermission, Permission
from ..serializers.driverDetailsSerializers import DriverSerializer, AdminDriverApprovalSerializer, DriverDraftSerializer, DriverPersonalDetailsViewSerializer, DocumentTypeSerializer, VerificationRequestSerializer, DriverVerificationPendingSerializer


class DynamicPermission(BasePermission):
    """
        DynamicPermission for all types of permissions.
    """
    def __init__(self, required_permissions):
        self.required_permissions = required_permissions

    def has_permission(self, request, view):
        role = request.user.role
        if role is None:
            return False
        if request.user.user_type != 'admin':
            return False
        permissions = RolePermission.objects.filter(role=role).first().permissions.values_list('permission_name', flat=True)
        required_permissions = self.required_permissions
        if bool(required_permissions in list(permissions)):
            return True
        return False


class DriverDetailsView(ListCreateAPIView):
    '''
        Submit driver details for verification using CreateAPIView.
    '''
    serializer_class = VerificationRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentType.objects.filter(deleted_at = None)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        document_serializer = DocumentTypeSerializer(queryset, many=True)
        data = {"data":document_serializer.data}
        return Response({
            "status": "success",
            "message": "Document types fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})  # Pass user in context

        if serializer.is_valid():
            serializer.save()
            data = {
                "status": "success",
                "message": "Details submitted for verification",
                "data" : "Driver details submitted successfully"}
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('user_view')]

    serializer_class = DriverSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name']

    ordering_fields = ['user__first_name', 'user__last_name', 'created_at', 'action_at']
    ordering = ['-created_at']

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        driver = DriverRequest.objects.filter(status = 'approved')
        if start_date:
            driver = driver.filter(created_at__date=start_date)
        return driver

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()

    #     if not queryset.exists():
    #         return Response({"status": "success", "message": "No Driver Found"}, status=200)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response({
    #         "status": "success",
    #         "message": "Drivers fetched successfully",
    #         "data": serializer.data
    #     }, status=200)


class AdminDriverStatusListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('user_view')]

    serializer_class = DriverVerificationPendingSerializer
    queryset = DriverRequest.objects.all()

    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]

    search_fields = ['user__first_name', 'user__last_name','status']
    filterset_fields = ['status']

    ordering_fields = ['user__first_name', 'user__last_name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        status = self.request.query_params.get('status')
        driver = DriverRequest.objects.all()
        if status:
            driver = driver.filter(status=status)

        if start_date:
            driver = driver.filter(created_at__date=start_date)

        return driver


class UserCountView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        customer_count = User.objects.filter(user_type='customer').count()
        driver_count = DriverDetail.objects.all().count()
        pending_driver_request_count = DriverRequest.objects.filter(status='pending').count()
        driverRequest = DriverRequest.objects.values_list('user_id', flat=True)
        draft_driver_request_count = User.objects.filter(user_type='driver').exclude(id__in=driverRequest).count()

        data = {
            "customer_count": customer_count,
            "driver_count": driver_count,
            "pending_driver_request_count": pending_driver_request_count,
            "draft_driver_request_count": draft_driver_request_count
        }

        return Response({
            "status": "success",
            "message": "User counts fetched successfully",
            "data": data
        }, status=status.HTTP_200_OK)


class DriverPersonalDetailsView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('user_view')]

    lookup_field = 'id'
    serializer_class = DriverPersonalDetailsViewSerializer

    def get_object(self):
        try:
            return DriverRequest.objects.get(id=self.kwargs['id'])
        except DriverRequest.DoesNotExist:
            return Response({"status" : "error", "message" :"Validation Error", "errors":{"user": "Does not applied as Driver."}}, status=status.HTTP_400_BAD_REQUEST)


class DriverDraftView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('user_view')]

    serializer_class = DriverDraftSerializer
    drivers = DriverRequest.objects.values_list('user_id', flat=True)
    queryset = User.objects.filter(user_type='driver').exclude(id__in=drivers)
    filter_backends = [OrderingFilter]
    ordering = ['created_at']


class AdminDriverApprovalView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission('user_edit')]

    lookup_field = 'id'
    serializer_class = AdminDriverApprovalSerializer

    def get_object(self):
        try:
            return DriverRequest.objects.get(id=self.kwargs['id'])
        except DriverRequest.DoesNotExist:
            return Response({"status" : "error", "message" :"Validation Error", "errors":{"user": "Does not applied as Driver."}}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        driver_request  = self.get_object()
        admin_user = request.user
        is_approved = request.data.get('is_approved')
        rejection_reason = request.data.get('rejection_reason')
        if is_approved:
            driver_request.status = 'approved'
            driver_request.action_by = admin_user
            driver_request.action_at = timezone.now()
            driver_request.save()

            driver_detail = DriverDetail.objects.create(
            user=driver_request.user,
            dob=driver_request.dob,
            verified_at=timezone.now(),
        )
            driver_detail.lang.set(driver_request.lang.all())
            driver_detail.verification_documents.set(driver_request.verification_documents.all())
            return Response({"status" : "success", "message" : 'Your Details are Approved.'}, status=status.HTTP_200_OK )

        if rejection_reason:
            driver_request.status = 'rejected'
            driver_request.rejection_reason = rejection_reason
            driver_request.action_by = admin_user
            driver_request.action_at = timezone.now()
            driver_request.save()
            data = {'Rejection reason': rejection_reason}
            return Response({"status" : "success" , 'message': 'Details rejected' , "data" : data}, status=status.HTTP_200_OK)
        return Response({"status" : "error", "message" :"Validation Error", "errors":{"user": "Please provide a rejection reason"}}, status=status.HTTP_400_BAD_REQUEST)


# class VerificationRequestResubmissionView(APIView):

#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         try:
#             driver = DriverDetail.objects.get(user=user)
#         except DriverDetail.DoesNotExist:
#             return Response({"status" : "error", "message" : "Driver details not found"}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = ResubmissionSerializer(driver, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save(user=user)
#             driver = DriverDetail.objects.get(user=user)
#             driver.status = 'pending'
#             driver.save()
#             return Response({"status" : "error", "data" : serializer.data}, status=status.HTTP_200_OK)
#         return Response({"status" : "error", "error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# class VerificationRequestResubmissionView(UpdateAPIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     queryset = DriverDetail.objects.all()
#     serializer_class = ResubmissionSerializer

#     def get_object(self):
#         user = self.request.user
#         return get_object_or_404(DriverDetail, user=user)

#     def update(self, request, *args, **kwargs):
#         driver = self.get_object()

#         serializer = self.get_serializer(driver, data=request.data, partial=True, context={'user': request.user})
#         if serializer.is_valid():
#             serializer.save()
#             driver.status = 'pending'
#             driver.save()
#             return Response({"status": "success", "data": serializer.data}, status=200)

#         return Response({"status": "error", "error": serializer.errors}, status=400)
