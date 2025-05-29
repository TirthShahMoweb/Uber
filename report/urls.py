from django.urls import path

from .views import reportViews



urlpatterns = [
    path('peakHoursReportView', reportViews.PeakHoursReportView.as_view()),
]
