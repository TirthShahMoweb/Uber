from django.urls import include, path
from rest_framework_simplejwt.views import \
    TokenObtainPairView  # Generates access & refresh token
from rest_framework_simplejwt.views import \
    TokenRefreshView  # Refreshes access token

from .views import (driverDetailsViews, languageViews, permissionViews,
                    rolesViews, tripViews, userViews)

# id name, mobile_number created_at status


urlpatterns = [
    # User Signup and Login
    path('login', userViews.LoginView.as_view()),
    path('signup', userViews.SignupView.as_view()),
    path('mobile_number', userViews.MobileNumberView.as_view()),
    path('otp-verification', userViews.OtpVerificationView.as_view()),
    path('resendOtpView', userViews.ResendOtpView.as_view()),
    path('addTeamMemberView', userViews.AddTeamMemberView.as_view()),
    path('listTeamMemberView', userViews.ListTeamMemberView.as_view()),
    path('destroyTeamMemberView/<int:pk>', userViews.DestroyTeamMemberView.as_view()),
    path('updateTeamMemberView/<int:pk>', userViews.UpdateTeamMemberView.as_view()),

    # Roles
    path('createRoles', rolesViews.CreateRoles.as_view()),
    path('retrieveUpdateDestroyRoles/<int:pk>', rolesViews.RetrieveUpdateDestroyRoles.as_view()),

    # path('AssignAdminRoleView/', userViews.AssignAdminRoleView.as_view()),
    path('adminRights/<str:verification_code>',userViews.adminRightsView.as_view()),
    path('roleListView', rolesViews.RoleListView.as_view()),

    # Permission
    path('createPermission', permissionViews.CreatePermission.as_view()),
    path('retrieveUpdateDestroyPermission/<int:pk>', permissionViews.RetrieveUpdateDestroyPermission.as_view()),

    # User Details
    path('updateProfileView', userViews.UpdateProfileView.as_view()),
    path('changePasswordView', userViews.ChangePasswordView.as_view()),
    path('forgotpassword', userViews.ForgotPasswordView.as_view()),
    path('forgot-password/<str:verification_code>', userViews.ResetPasswordView.as_view()),
    path('ProfileView', userViews.ProfileView.as_view()),

    # Driver Details
    path('adminDriverStatusList', driverDetailsViews.AdminDriverStatusListView.as_view()),
    path('add-driver-details', driverDetailsViews.DriverDetailsView.as_view()),
    path('admin-verify-driver/<int:id>', driverDetailsViews.AdminDriverApprovalView.as_view(), name = 'driver-verification-approval'),
    # path('driver-details/resubmit', driverDetailsViews.VerificationRequestResubmissionView.as_view(), name = 'resubmission'),
    path('ImpersonationView', driverDetailsViews.ImpersonationView.as_view()),
    path('driverPersonalDetailView/<int:id>', driverDetailsViews.DriverPersonalDetailsView.as_view()),
    path('driverDraftView', driverDetailsViews.DriverDraftView.as_view()),
    path('driverListView', driverDetailsViews.DriverListView.as_view()),
    path('languagesListView', languageViews.LanguageListView.as_view()),
    path('userCountView', driverDetailsViews.UserCountView.as_view()),
    path('updateDriverLastOnlineAtView', userViews.UpdateDriverLastOnlineAtView.as_view()),
    # path('driverTripPendingView', driverDetailsViews.DriverTripPendingView.as_view(), name='driver_trip_pending'),
    path('tripHistoryView', userViews.TripHistoryView.as_view()),

    # Trip Details
    path('tripDetails', tripViews.TripDetails.as_view()),
    path('addTripDetails', tripViews.AddTripDetails.as_view(), name='add_trip'),
    path('tripCancelView/<int:id>', tripViews.TripCancelView.as_view()),
    path("tripApprovalView/<int:id>", tripViews.TripApprovalView.as_view()),
    path("reachedPickUpLocationView/<int:id>", tripViews.ReachedPickUpLocationView.as_view()),
    path("verifiedDriverAtPickUpLocationView/<int:id>", tripViews.VerifiedDriverAtPickUpLocationView.as_view()),
    path("tripCompletedView/<int:id>", tripViews.TripCompletedView.as_view()),
    path("feedbackRatingView/<int:id>", tripViews.FeedbackRatingView.as_view()),
    path('paymentListView', tripViews.PaymentListView.as_view()),

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