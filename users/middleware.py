from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from pprint import pprint
import re
from companies.url_variables import Full_URL_PATHS_WITHOUT_ARGUMENTS


public_urls = [
    re.compile(r'^/favicon.(svg|ico)$'),
    re.compile(r'^/companies/SA/data_collection/(auth|create)_for_client/.*'),
    re.compile(r'^/accounts/public_tax_report/\d+/(?:[0-9a-fA-F]+\-?)+/$')
]

class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = reverse('users_login')
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        next_url = request.GET.get('next')
        if not next_url:
            next_url = request.POST.get('next')

        # This is for the data collection page which is public
        is_public_url = False
        for url in public_urls:
            if url.match(request.path):
                is_public_url = True
                break
        
        if is_public_url:
            pass
        elif not request.user.is_authenticated and request.path != self.login_url:
            return redirect(f"{self.login_url}?next={next_url or request.path}")
        
        # render the page if the user is authenticated or the page is public
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
