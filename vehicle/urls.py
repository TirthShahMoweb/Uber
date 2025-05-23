from django.urls import include, path
# from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import \
    TokenObtainPairView  # Generates access & refresh token
from rest_framework_simplejwt.views import \
    TokenRefreshView  # Refreshes access token

from vehicle.views import vehicleViews

# router = DefaultRouter()
# router.register(r'resetpassword', UserViews.ResetPassword, basename='ResetPassword')
# urlpatterns = router.urls
urlpatterns = [
    # Vehicle Details
    path('addVehicleView', vehicleViews.addVehicleView.as_view()),
    path('adminVehicleStatusListView', vehicleViews.AdminVehicleStatusListView.as_view()),
    path('driverVehicleDetailsView/<int:pk>', vehicleViews.DriverVehicleDetailsView.as_view()),
    path('vehicleListView', vehicleViews.VehicleListView.as_view()),
    path('adminVehicleApprovalView/<int:pk>', vehicleViews.AdminVehicleApprovalView.as_view()),
    path('draftVehicleListView', vehicleViews.DraftVehicleListView.as_view()),
    path('driverVehiclesListView', vehicleViews.DriverVehiclesListView.as_view()),
    path('selectVehicleView', vehicleViews.SelectVehicleView.as_view()),
    # path('vehicleListView', vehicleViews.VehicleListView.as_view()),
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