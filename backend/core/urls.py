from django.urls import path
from .views import FileUploadView, HistoryView, PDFReportView
from core.views import create_admin_user

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:pk>/', PDFReportView.as_view(), name='pdf-report'), # New PDF Route
    path('create-secret-admin/', create_admin_user),
]