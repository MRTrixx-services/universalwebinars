"""
URL configuration for dailyrespond project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from live_webinars.sitemaps import WebinarSitemap

sitemaps = {
    'webinars': WebinarSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("home.urls")),
    path("live-webinars/", include("live_webinars.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("recorded-webinars/", include("recorded_webinars.urls")),
    path("accounts/", include("accounts.urls")),
    path("cart/",include("cart.urls")),
    path("orders/",include("orders.urls")),
    path("profile/", include("profile.urls")),
    path("admin-panel/", include("adminpanel.urls")),
    path("integrations/", include("integrations.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )