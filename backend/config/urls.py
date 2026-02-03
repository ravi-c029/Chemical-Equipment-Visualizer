from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import create_admin_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')), # Include our core app URLs here
    path('fix-admin/', create_admin_user), 
]


# This is required to serve the uploaded CSV files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)