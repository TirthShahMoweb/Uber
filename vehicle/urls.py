from django.urls import path, include
from vehicle.views import VehicleViews
# from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access & refresh token
    TokenRefreshView      # Refreshes access token
)
# router = DefaultRouter()
# router.register(r'resetpassword', UserViews.ResetPassword, basename='ResetPassword')
# urlpatterns = router.urls
urlpatterns = [
    # Vehicle Details
    path('addVehicleView', VehicleViews.addVehicleView.as_view()),
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