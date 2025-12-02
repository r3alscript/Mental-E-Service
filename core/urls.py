from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authorization.urls')),
    path('booking/', include('booking.urls')),
    path('profile/', include('profiles.urls')),
    path('chat/', include('chat.urls')),
    path("hotlines/", include('hotlines.urls'), name="hotlines")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)