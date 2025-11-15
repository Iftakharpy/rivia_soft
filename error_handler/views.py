from .error_reporting import safe_render_error_page
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
  return safe_render_error_page(
    request = request,
    template_name = 'error_handler/error.html',
    status = 500,
    context = context,
    )
