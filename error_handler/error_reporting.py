import sys
import uuid
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseServerError
from django.views.debug import ExceptionReporter

# Use the same logger name so messages are consistent.
logger = logging.getLogger('django')

from companies.url_variables import *
Navbar_links = {
  'home': f'{APPLICATION_NAME}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}


def save_exception_report(request, exception):
	"""
	A standalone utility function that generates and saves the full Django
	debug page for a given exception.

	This can be called from anywhere that has access to the request object
	and the exception, such as middleware or a custom error handler view.
	"""

	unique_id = uuid.uuid4().hex[:8]
	timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	filename = f"error_{timestamp}_{unique_id}.html"
	
	settings.ERROR_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
	filepath:Path = settings.ERROR_REPORTS_DIR / filename

	try:
		# Use Django's ExceptionReporter to get the full HTML traceback page.
		reporter = ExceptionReporter(request, *sys.exc_info())
		html_report = reporter.get_traceback_html()
		
		with open(filepath, 'w', encoding='utf-8') as f:
			f.write(html_report)
		
		# Log a concise message pointing to the full report.
		logger.critical(f"ERROR_REPORT: {filepath}", exc_info=True)
	except Exception as e:
		# Failsafe: If saving the report fails, log that the report could not be created.
		logger.error(f"ERROR_REPORT_FAILURE: Couldn't save error report.", exc_info=True)

def safe_render_error_page(request, template_name: str, status: int, context: Optional[dict] = None):
	"""
	A robust helper function to render an error template.

	If rendering the specified template fails for any reason, it logs the
	"meta-error" critically and returns a hardcoded, failsafe HTTP 500
	response to ensure the user always sees something.

	Args:
		request: The Django request object.
		template_name: The path to the error template (e.g., 'errors/404.html').
		status: The HTTP status code to return with the rendered template.
		context: An optional dictionary of context data to pass to the template.
	"""
	if context is None:
		context = {
			**Navbar_links
		}
		
	try:
		# The primary action: attempt to render the specified error template.
		return render(request, template_name, context, status=status)
	except Exception as e:
		# THE FAILSAFE: This block executes if the template is broken.
		logger.critical(f"ERROR_TEMPLATE: '{template_name}' template is broken.",
						exc_info=True) # This attaches the full traceback of the template error.

		save_exception_report(request, e)
		return HttpResponseServerError(
			f"""<h1>Server Error (500)</h1>
			<p>A critical error occurred while trying to display an error page.</p>""",
			content_type="text/html"
		)




# Old error logger
import traceback
from datetime import datetime, timezone

def log_server_error_to_file(e=None):
	# Get exception details
	type_, value, tb = sys.exc_info()
	formatted_traceback = "".join(traceback.format_exception(type_, value, tb))

	# Get current timestamp in UTC format
	timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 format

	# Write the error details to the log file
	with open(settings.ERROR_LOG_FILE_PATH, 'a+') as f:
		f.write(f"[{timestamp} UTC] {type_}: {value}\n")
		f.write(f"{'='*35}\n")
		f.write(formatted_traceback)
		f.write(f"{'='*35}\n")
		f.write(f"\n\n\n")
