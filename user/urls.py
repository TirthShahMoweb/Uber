from django.urls import path, include
from .views import UserViews, DriverDetailsViews, LanguageViews, RolesViews, PermissionViews, VehicleViews
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh token
    TokenRefreshView      # Refreshes access token
)


urlpatterns = [
    # User Signup and Login
    path('login/', UserViews.LoginView.as_view()),
    path('signup/', UserViews.SignupView.as_view()),
    path('addTeamMemberView/', UserViews.AddTeamMemberView.as_view()),
    path('mobile_number/', UserViews.Mobile_Number.as_view()),
    path('otp-verification/', UserViews.OtpVerificationView.as_view()),


    # Roles
    path('createRoles/', RolesViews.CreateRoles.as_view()),
    path('RetrieveUpdateDestroyRoles/<int:pk>/', RolesViews.RetrieveUpdateDestroyRoles.as_view()),
    path('AssignAdminRoleView/', UserViews.AssignAdminRoleView.as_view()),

    # Permission
    path('createPermission/', PermissionViews.CreatePermission.as_view()),
    path('RetrieveUpdateDestroyPermission/<int:pk>/', PermissionViews.RetrieveUpdateDestroyPermission.as_view()),

    # User Details
    path('updateprofile/<str:verification_code>/', UserViews.updateprofile.as_view()),
    path('resetpassword/<str:verification_code>/', UserViews.ResetPassword.as_view()),
    path('forgotpassword/', UserViews.forgot_password.as_view()),
    path('forgot-password/<str:verification_code>/', UserViews.change_password.as_view()),

    # Driver Details
    path('adminDriverApprovalPendingList/', DriverDetailsViews.AdminDriverApprovalPendingList.as_view()),
    path('add-driver-details/', DriverDetailsViews.DriverDetailsView.as_view()),
    path('admin-verify-driver/<int:pk>/', DriverDetailsViews.AdminDriverApprovalView.as_view(), name = 'driver-verification-approval'),
    path('driver-details/resubmit/', DriverDetailsViews.VerificationRequestResubmissionView.as_view(), name = 'resubmission'),

    path('languagesListView/', LanguageViews.LanguageListView.as_view()),

    # # Vehicle Details
    # path('addVehicle/', VehicleViews.addVehicleView.as_view()),
    # path('adminVehicleApprovalPendingList/', VehicleViews.displayVerificationList.as_view()),
    # path('admin-verify-vehicle/<int:pk>/', VehicleViews.vehicleverificationRequest.as_view(),name = 'vehicle-verification-approval'),
    # path('resubmitVehicleView/<int:pk>/', VehicleViews.resubmitVehicleView.as_view(), name = 'vehicle-resubmission'),
    # path('vehicleDetails/', VehicleViews.VehicleDetailsView.as_view()),
    # # path('selectVehicle/<int:pk>', VehicleViews.VehicleDetailsView.as_view(), name = 'Select_vehicle'),
    # path('deleteVehicleView/<int:pk>/', VehicleViews.VehicleDestroyView.as_view()),

    # Token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]