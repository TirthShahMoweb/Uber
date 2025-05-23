from django.db.models import Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from utils.mixins import DynamicPermission

from ..models import (
    DocumentType,
    DriverDetail,
    DriverRequest,
    Payment,
    Role,
    Trip,
    User,
)
from ..serializers.driverDetailsSerializers import (
    AdminDriverApprovalSerializer,
    DocumentTypeSerializer,
    DriverDraftSerializer,
    DriverPersonalDetailsViewSerializer,
    DriverSerializer,
    DriverVerificationPendingSerializer,
    ImpersonationSerializer,
    VerificationRequestSerializer,
)


class ImpersonationPermission(BasePermission):
    """
    Permission class to check if the user has permission to impersonate another user.
    """

    def has_permission(self, request, view):
        role = request.user.role
        if role is None:
            return False
        if request.user.user_type != "admin":
            return False
        role = (
            Role.objects.filter(id=role.id).values_list("role_name", flat=True).first()
        )
        if role == "CEO":
            return True
        return False


class DriverDetailsView(ListCreateAPIView):
    """
    Submit driver details for verification using CreateAPIView.
    """

    serializer_class = VerificationRequestSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DocumentType.objects.filter(deleted_at=None)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        document_serializer = DocumentTypeSerializer(queryset, many=True)
        data = {"data": document_serializer.data}
        return Response(
            {
                "status": "success",
                "message": "Document types fetched successfully",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(
            data=request.data, context={"user": user}
        )  # Pass user in context

        if serializer.is_valid():
            serializer.save()
            data = {
                "status": "success",
                "message": "Details submitted for verification",
                "data": "Driver details submitted successfully",
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverListView(ListAPIView):
    """
    Driver List
    """

    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission("user_view")]

    serializer_class = DriverSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["user__first_name", "user__last_name"]

    ordering_fields = ["user__first_name", "user__last_name", "created_at", "action_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        driver = DriverRequest.objects.filter(status="approved")
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
    """
    Admin Driver Status List
    """

    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission("user_view")]

    serializer_class = DriverVerificationPendingSerializer
    queryset = DriverRequest.objects.all()

    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]

    search_fields = ["user__first_name", "user__last_name", "status"]
    filterset_fields = ["status"]

    ordering_fields = ["user__first_name", "user__last_name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        status = self.request.query_params.get("status")
        driver = DriverRequest.objects.all()
        if status:
            driver = driver.filter(status=status)

        if start_date:
            driver = driver.filter(created_at__date=start_date)

        return driver


class UserCountView(ListAPIView):
    """
    User Count
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        customer_count = User.objects.filter(user_type="customer").count()
        driver_count = DriverDetail.objects.all().count()
        pending_driver_request_count = DriverRequest.objects.filter(
            status="pending"
        ).count()
        driver_request = DriverRequest.objects.values_list("user_id", flat=True)
        draft_driver_request_count = (
            User.objects.filter(user_type="driver")
            .exclude(id__in=driver_request)
            .count()
        )
        total_successfull_trip = Trip.objects.filter(status="Completed").count()
        total_number_payment_pending = Payment.objects.filter(status="pending").count()
        total_amount_pending = Payment.objects.filter(status="pending").aggregate(
            amount=Sum("amount")
        )
        print(total_amount_pending["amount"])

        data = {
            "customer_count": customer_count,
            "driver_count": driver_count,
            "pending_driver_request_count": pending_driver_request_count,
            "draft_driver_request_count": draft_driver_request_count,
            "total_successfull_trip": total_successfull_trip,
            "total_number_payment_pending": total_number_payment_pending,
            "total_amount_pending": total_amount_pending["amount"],
        }

        return Response(
            {
                "status": "success",
                "message": "User counts fetched successfully",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


class DriverPersonalDetailsView(RetrieveAPIView):
    """
    Driver Personal Details
    """

    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission("user_view")]

    lookup_field = "id"
    serializer_class = DriverPersonalDetailsViewSerializer

    def get_object(self):
        try:
            return DriverRequest.objects.get(id=self.kwargs["id"])
        except DriverRequest.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Validation Error",
                    "errors": {"user": "Does not applied as Driver."},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class DriverDraftView(ListAPIView):
    """
    Draft Driver
    """

    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission("user_view")]

    serializer_class = DriverDraftSerializer
    drivers = DriverRequest.objects.values_list("user_id", flat=True)
    queryset = User.objects.filter(user_type="driver").exclude(id__in=drivers)
    filter_backends = [OrderingFilter]
    ordering = ["created_at"]


class AdminDriverApprovalView(UpdateAPIView):
    """
    Admin Driver Approval
    """

    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        return [IsAuthenticated(), DynamicPermission("user_edit")]

    lookup_field = "id"
    serializer_class = AdminDriverApprovalSerializer

    def get_object(self):
        try:
            return DriverRequest.objects.get(id=self.kwargs["id"])
        except DriverRequest.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Validation Error",
                    "errors": {"user": "Does not applied as Driver."},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        driver_request = self.get_object()
        admin_user = request.user
        is_approved = request.data.get("is_approved")
        rejection_reason = request.data.get("rejection_reason")
        if is_approved:
            driver_request.status = "approved"
            driver_request.action_by = admin_user
            driver_request.action_at = timezone.now()
            driver_request.save()

            driver_detail = DriverDetail.objects.create(
                user=driver_request.user,
                dob=driver_request.dob,
                verified_at=timezone.now(),
            )
            driver_detail.lang.set(driver_request.lang.all())
            driver_detail.verification_documents.set(
                driver_request.verification_documents.all()
            )
            return Response(
                {"status": "success", "message": "Your Details are Approved."},
                status=status.HTTP_200_OK,
            )

        if rejection_reason:
            driver_request.status = "rejected"
            driver_request.rejection_reason = rejection_reason
            driver_request.action_by = admin_user
            driver_request.action_at = timezone.now()
            driver_request.save()
            data = {"Rejection reason": rejection_reason}
            return Response(
                {"status": "success", "message": "Details rejected", "data": data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "status": "error",
                "message": "Validation Error",
                "errors": {"user": "Please provide a rejection reason"},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ImpersonationView(CreateAPIView):
    """
        Impersonation
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ImpersonationPermission]

    serializer_class = ImpersonationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # Pass user in context

        if serializer.is_valid():
            impersonation_type  = request.data.get("type")
            if impersonation_type  == "driver":
                driver = DriverRequest.objects.filter(id=request.data["id"]).first()
                user = driver.user

            if impersonation_type  == "admin":
                user = User.objects.filter(id=request.data["id"]).first()

            refresh = RefreshToken.for_user(user)
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.user_type,
            }

            return Response(
                {
                    "status": "success",
                    "message": "Impersonation request submitted successfully",
                    "data": data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
