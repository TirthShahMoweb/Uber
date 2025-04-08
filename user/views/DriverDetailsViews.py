from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..models import DriverDetail, DocumentType, User
from ..serializers.DriverDetailsSerializers import DriverSerializer, AdminDriverApprovalSerializer, DriverDraftSerializer, DriverDetailsApprovalPendingSerializer, DocumentTypeSerializer, VerificationRequestSerializer, DriverVerificationPendingSerializer, ResubmissionSerializer

class CanVerifyDriver(BasePermission):
    """
    Custom permission to allow only users with a role having specific permissions to verify drivers.
    """

    def has_permission(self, request, view):
        role = request.user.role
        if role is None:
            return False
        # role_permissions = AdminPermission.objects.filter(role=role).first().permissions.values_list('permission_name', flat=True)
        required_permissions = {"Full Access", "View and Manage Operations", "Review Content and Features"}
        # return bool(set(role_permissions) & required_permissions)
        return bool(required_permissions)


class DriverDetailsView(ListCreateAPIView):
    '''
        Submit driver details for verification using CreateAPIView.
    '''
    serializer_class = VerificationRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Fetch required document types (used for GET requests)
        return DocumentType.objects.filter(deleted_at = None)

    def list(self, request, *args, **kwargs):
        # Handle the GET request to list document types
        queryset = self.get_queryset()
        document_serializer = DocumentTypeSerializer(queryset, many=True)
        return Response({
            "status": "success",
            "required_documents": document_serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})  # Pass user in context

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Details submitted for verification"
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DriverList(ListAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    serializer_class = DriverSerializer
    queryset = DriverDetail.objects.filter(status='approved')
    filter_backends = [SearchFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__mobile_number']

    ordering_fields = ['user__first_name', 'user__last_name', 'created_at', 'verified_at']


    ordering_fields = ['user__first_name', 'user__last_name', 'created_at','verified_at']
    ordering = ['-created_at']


class AdminDriverApprovalPendingList(ListAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    serializer_class = DriverVerificationPendingSerializer
    queryset = DriverDetail.objects.all()

    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]

    search_fields = ['user__first_name', 'user__last_name','status']
    filterset_fields = ['status']

    ordering_fields = ['user__first_name', 'user__last_name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        # end_date = self.request.query_params.get('end_date')
        status = self.request.query_params.get('status', 'pending')
        driver = DriverDetail.objects.filter(status=status)
        if start_date:
            driver = driver.filter(created_at__date=start_date)
        return driver


class DriverDetailsApprovalPendingView(RetrieveAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    lookup_field = 'verification_code'

    serializer_class = DriverDetailsApprovalPendingSerializer

    def get_object(self):
        try:
            user = User.objects.get(verification_code=self.kwargs['verification_code'])
            return DriverDetail.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"status" : "error", "message" : "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        except DriverDetail.DoesNotExist:
            return Response({"status" : "error", "message" : "Does not applied as Driver."}, status=status.HTTP_400_BAD_REQUEST)


class DriverDraftView(ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DriverDraftSerializer
    queryset = User.objects.filter(user_type='driver').exclude(id__in=DriverDetail.objects.values_list('user_id', flat=True))
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering = ['created_at']


class AdminDriverApprovalView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'verification_code'
    serializer_class = AdminDriverApprovalSerializer

    def get_object(self):
        try:
            user = User.objects.get(verification_code=self.kwargs['verification_code'])
            return DriverDetail.objects.get(user=user)
        except User.DoesNotExist:
            return Response({"status" : "error", "message" : "User not found."}, status=status.HTTP_400_BAD_REQUEST)
        except DriverDetail.DoesNotExist:
            return Response({"status" : "error", "message" : "Does not applied as Driver."}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
        driver = self.get_object()
        is_approved = request.data['is_approved']
        rejection_reason = request.data['rejection_reason']
        if is_approved:
            driver.status = 'approved'
            driver.verified_at = timezone.now()
            driver.save()
            return Response({"status" : "error", "message" : 'Your Details are Approved.'}, status=status.HTTP_400_BAD_REQUEST)

        if rejection_reason:
            driver.status = 'rejected'
            driver.rejection_reason = rejection_reason
            driver.save()
            data = {'message': 'Details rejected', 'Rejection reason': rejection_reason}
            return Response({"status" : "success" , "data" : data}, status=status.HTTP_200_OK)
        return Response({"status" : "fail", "message" : 'Please provide a rejection reason'}, status=status.HTTP_400_BAD_REQUEST)


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


class VerificationRequestResubmissionView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = DriverDetail.objects.all()
    serializer_class = ResubmissionSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(DriverDetail, user=user)

    def update(self, request, *args, **kwargs):
        driver = self.get_object()

        serializer = self.get_serializer(driver, data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            driver.status = 'pending'
            driver.save()
            return Response({"status": "success", "data": serializer.data}, status=200)

        return Response({"status": "error", "error": serializer.errors}, status=400)