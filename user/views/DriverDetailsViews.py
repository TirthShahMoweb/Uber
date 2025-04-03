from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..models import DriverDetail, AdminPermission, DocumentType
from ..serializers.DriverDetailsSerializers import DocumentTypeSerializer, VerificationRequestSerializer, VerificationPendingSerializer, ResubmissionSerializer

class CanVerifyDriver(BasePermission):
    """
    Custom permission to allow only users with a role having specific permissions to verify drivers.
    """

    def has_permission(self, request, view):
        role = request.user.role
        if role is None:
            return False
        role_permissions = AdminPermission.objects.filter(role=role).first().permissions.values_list('permission_name', flat=True)
        required_permissions = {"Full Access", "View and Manage Operations", "Review Content and Features"}
        return bool(set(role_permissions) & required_permissions)


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


class AdminDriverApprovalPendingList(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanVerifyDriver]

    serializer_class = VerificationPendingSerializer
    queryset = DriverDetail.objects.filter(status='pending').annotate(driver_name=Concat(F('user__first_name'), Value(' '), F('user__last_name')))


class AdminDriverApprovalView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, CanVerifyDriver]

    def post(self, request, pk):
        try:
            verification_request = DriverDetail.objects.get(pk=pk)
        except DriverDetail.DoesNotExist:
            return Response({"status" : "error", "message" : 'Verification request not found'}, status=status.HTTP_400_BAD_REQUEST)

        is_approved = request.data.get("is_approved")
        rejection_reason = request.data.get("rejection_reason")

        if is_approved:
            verification_request.status = 'approved'
            verification_request.verified_at = timezone.now()
            verification_request.save()
            return Response({"status" : "error", "message" : 'Details approved and moved to DriverDetails'}, status=status.HTTP_400_BAD_REQUEST)

        if rejection_reason:
            verification_request.status = 'rejected'
            verification_request.rejection_reason = rejection_reason
            verification_request.save()
            data = {'message': 'Details rejected', 'Rejection reason': rejection_reason}
            return Response({"status" : "success" , "data" : data}, status=status.HTTP_200_OK)
        return Response({"status" : "fail", "message" : 'Please provide a rejection reason'}, status=status.HTTP_400_BAD_REQUEST)


class VerificationRequestResubmissionView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            driver = DriverDetail.objects.get(user=user)
        except DriverDetail.DoesNotExist:
            return Response({"status" : "error", "message" : "Driver details not found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResubmissionSerializer(driver, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=user)
            driver = DriverDetail.objects.get(user=user)
            driver.status = 'pending'
            driver.save()
            return Response({"status" : "error", "data" : serializer.data}, status=status.HTTP_200_OK)
        return Response({"status" : "error", "error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VerificationRequestResubmissionView(UpdateAPIView):
    queryset = DriverDetail.objects.all()
    serializer_class = ResubmissionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the DriverDetail for the authenticated user
        user = self.request.user
        return get_object_or_404(DriverDetail, user=user)

    def update(self, request, *args, **kwargs):
        # Get the instance for resubmission
        driver = self.get_object()

        # Pass the data and allow partial updates
        serializer = self.get_serializer(driver, data=request.data, partial=True, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            # Update the status to 'pending'
            driver.status = 'pending'
            driver.save()
            return Response({"status": "success", "data": serializer.data}, status=200)

        return Response({"status": "error", "error": serializer.errors}, status=400)
