"""rivia_soft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

from companies.url_variables import URL_NAMES_PREFIXED_WITH_APP_NAME


urlpatterns = [
    path('', lambda *args, **kwargs:redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name)),
    path('companies/', include('companies.urls'), name='companies'),
    path('accounts/', include('accounts.urls'), name='accounts'),
    path('u/', include('users.urls')),
    path('invoice/', include('invoice.urls'), name='invoice'),
    path('only-admins-can-access-this/', admin.site.urls, name='admin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # urlpatterns += staticfiles_urlpatterns()


# Custom error handler page
handler400 = 'error_handler.views.handle_400_error'
handler403 = 'error_handler.views.handle_403_error'
handler404 = 'error_handler.views.handle_404_error'
handler500 = 'error_handler.views.handle_500_error'

# Change admin titles and headers
admin.site.site_header = "Rivia Solutions"
admin.site.site_title = "Rivia Solutions Administration"
admin.site.index_title = "Welcome to RSA"
