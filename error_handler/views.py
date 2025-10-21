from pathlib import Path
from django.http.response import Http404, HttpResponseBadRequest
from django.shortcuts import render

from companies.url_variables import *
from error_handler.error_logger import log_server_error_to_file


Navbar_links = {
  'home': f'{APPLICATION_NAME}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}

# Create your views here.
def handle_400_error(request, exception):
  context = {
    **Navbar_links,
    'error_code': 400,
    'message': 'Bad Request',
    'hint': "Server can't/won't process the request due to client error. \
Don't repeat this request without modification."
  }
  return render(
    request = request,
    template_name = 'error_handler/error.html',
    context = context,
    status = 400)

def handle_403_error(request, exception):
  context = {
    **Navbar_links,
    'error_code': 403,
    'message': 'Forbidden',
    'hint': "You are unauthorized to access this."
  }
  return render(
    request = request,
    template_name = 'error_handler/error.html',
    context = context,
    status = 403)

def handle_404_error(request, exception):
  context = {
    **Navbar_links,
    'error_code': 404,
    'message': 'Not Found',
    'hint': "Requested content can't be found in the server."
  }
  return render(
    request = request,
    template_name = 'error_handler/error.html',
    context = context,
    status = 404)


def handle_500_error(request):
  context = {
    **Navbar_links,
    'error_code': 500,
    'message': 'Internal Server Error',
    'hint': "This is an edge case contact the developer."
  }

  # Log 500 errors to file
  log_server_error_to_file()

  return render(
    request = request,
    template_name = 'error_handler/error.html',
    context = context,
    status = 500)
