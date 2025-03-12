import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from django.http.response import Http404, HttpResponseBadRequest
from django.shortcuts import render

from companies.url_variables import *


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
  
  # Get exception details
  type_, value, tb = sys.exc_info()
  formatted_traceback = "".join(traceback.format_exception(type_, value, tb))

  # Get current timestamp in UTC format
  timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 format

  # Define log file path
  file_path = Path(__file__)
  file_path = file_path / r"../500_errors.log"

  # Write the error details to the log file
  with open(file_path, 'a+') as f:
    f.write(f"[{timestamp} UTC] {type_.__name__}: {value}\n")
    f.write(f"{'='*35}\n")
    f.write(formatted_traceback)
    f.write(f"{'='*35}\n")
    f.write(f"\n\n\n")
  
  return render(
    request = request,
    template_name = 'error_handler/error.html',
    context = context,
    status = 500)
