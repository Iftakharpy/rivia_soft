import logging
from django.conf import settings

from .error_reporting import safe_render_error_page
from ses_mailer.boto import SES_MAILER

from companies.url_variables import *
Navbar_links = {
  'home': f'{APPLICATION_NAME}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}


# Get a logger for this module.
logger = logging.getLogger(__name__)


# Create your views here.
def handle_400_error(request, exception):
  context = {
    **Navbar_links,
    'error_code': 400,
    'message': 'Bad Request',
    'hint': "Server can't/won't process the request due to client error. \
Don't repeat this request without modification."
  }
  return safe_render_error_page(
    request = request,
    template_name = 'error_handler/error.html',
    status = 400,
    context = context,
    )

def handle_403_error(request, exception):
  context = {
    **Navbar_links,
    'error_code': 403,
    'message': 'Forbidden',
    'hint': "You are unauthorized to access this."
  }
  return safe_render_error_page(
    request = request,
    template_name = 'error_handler/error.html',
    status = 403,
    context = context,
    )

def handle_404_error(request, exception):
  context = {
    **Navbar_links,
    'error_code': 404,
    'message': 'Not Found',
    'hint': "Requested content can't be found in the server."
  }
  return safe_render_error_page(
    request = request,
    template_name = 'error_handler/error.html',
    status = 404,
    context = context,
    )


def handle_500_error(request):
  context = {
    **Navbar_links,
    'error_code': 500,
    'message': 'Internal Server Error',
    'hint': "This is an edge case contact the developer."
  }

  SES_MAILER.send_email(
    sender=settings.DEFAULT_FROM_EMAIL,
    to_addresses=['Admin <iftakharhusan7@gmail.com>'],
    reply_to_addresses=[settings.DEFAULT_REPLY_TO_EMAIL],
    subject=f"Server error",
    body_text=f"check the server logs an unexpected error occurred"
    )

  return safe_render_error_page(
    request = request,
    template_name = 'error_handler/error.html',
    status = 500,
    context = context,
    )
