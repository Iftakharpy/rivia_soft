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
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.shortcuts import render

from companies.url_variables import URL_NAMES_PREFIXED_WITH_APP_NAME
from ses_mailer.views import ses_sns_webhook



urlpatterns = [
	path('', lambda *args, **kwargs:redirect(URL_NAMES_PREFIXED_WITH_APP_NAME.Merged_Tracker_home_name)),
	path('u/', include('users.urls')),
	path('companies/', include('companies.urls'), name='companies'),
	path('accounts/', include('accounts.urls'), name='accounts'),
	path('invoice/', include('invoice.urls'), name='invoice'),
	path('only-admins-can-access-this/', admin.site.urls, name='admin'),
	path('aws/ses_to_sns_email_events/', ses_sns_webhook, name='ses_sns_webhook'),
	re_path(r"^favicon?.(svg|ico)", lambda *args,**kwargs:redirect("/static/logos/bimi.svg", permanent=True)),
]

# When DEBUG=False; DEBUG_PRODUCTION_SETTING_LOCALLY=True (optional)
#   `python .\manage.py runserver --insecure` can be used to serve static files for local testing
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def trigger__500(*args, **kwargs):
	raise Exception("Intentional server error")
def trigger__template_error(request,*args, **kwargs):
	return render(request, '__template_raises_error.html')

if settings.ENABLE_ERROR_TRIGGERS: # These are only for testing purposes 
	urlpatterns += [
		path('trigger__500', trigger__500),
		path('trigger__template_error', trigger__template_error),
	]


# Custom error handler page
handler400 = 'error_handler.views.handle_400_error'
handler403 = 'error_handler.views.handle_403_error'
handler404 = 'error_handler.views.handle_404_error'
handler500 = 'error_handler.views.handle_500_error'

# Change admin titles and headers
admin.site.site_header = "Rivia Solutions"
admin.site.site_title = "Rivia Solutions Administration"
admin.site.index_title = "Welcome to RSA"
