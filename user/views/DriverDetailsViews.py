from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView


from django.db.models import F, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django.urls import reverse

from ..models import DriverDetail, AdminPermission
from ..serializers.DriverDetailsSerializers import VerificationRequestSerializer, VerificationPendingSerializer, ResubmissionSerializer

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


class DriverDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = VerificationRequestSerializer(data=request.data, context = {'user': user})
        data=request.data
        if serializer.is_valid():
            serializer.save(user=user)
            # user = User.objects.get(pk=data['user'])
            # user.USER_TYPES = 'driver'
            # user.save()

            return Response({"status" : "success",'message': 'Details submitted for verification'}, status=status.HTTP_201_CREATED)
        return Response({"status" : "error", "error" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
            # Log rejection details
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
