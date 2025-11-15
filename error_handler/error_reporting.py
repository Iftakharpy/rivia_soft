import sys
import uuid
import logging
import traceback
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponseServerError
from django.views.debug import ExceptionReporter

from ses_mailer.boto import SES_MAILER
from users.models import CustomUser
from companies.url_variables import *


# Use the same logger name so messages are consistent.
logger = logging.getLogger('django')

Navbar_links = {
  'home': f'{APPLICATION_NAME}:home',

  **Full_URL_PATHS_WITHOUT_ARGUMENTS.get_dict(),
  **URL_NAMES_PREFIXED_WITH_APP_NAME.get_dict()
}




def get_formatted_error():
	# Get exception details
	type_, value, tb = sys.exc_info()
	formatted_traceback = "".join(traceback.format_exception(type_, value, tb))

	# Get current timestamp in UTC format
	timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 format
	
	return f"""[{timestamp} UTC] {type_}: {value}

{'='*35}
{formatted_traceback}
{'='*35}

"""

def alert_admins(subject:str, body_text:str|None=None):
	if settings.DISABLE_ADMIN_EMAIL_ALERTS:
		print(f"\n\nEmail: {subject}\nBody:{body_text}\n\n")
		return
	
	# Prepare recipients
	to_addresses = set(settings.ADMIN_EMAILS)
	if settings.ADMIN_EMAILS_EXTEND_WITH_SUPERUSER:
		to_addresses.update(CustomUser.get_active_superusers_emails())

	try:
		SES_MAILER.send_email(
			sender=settings.DEFAULT_FROM_EMAIL,
			to_addresses=list(to_addresses),
			reply_to_addresses=[settings.DEFAULT_REPLY_TO_EMAIL],
			subject=subject,
			body_text=body_text or get_formatted_error()
		)
	except Exception as e:
		logger.critical(f"Failed sending email, disabling admin alerts", exc_info=e)
		settings.DISABLE_ADMIN_EMAIL_ALERTS = True


def save_exception_report(request, exception) -> Path|None:
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
		alert_admins(
			subject="Error occurred, check server logs for details",
			body_text=f"""ERROR_REPORT: {filepath}\n\n{get_formatted_error()}"""
			)
		return filepath
	except Exception as e:
		# Failsafe: If saving the report fails, log that the report could not be created.
		logger.error(f"ERROR_REPORT_FAILURE: Couldn't save error report.", exc_info=True)
		alert_admins(
			subject="FATAL: Couldn't save error report. Needs immediate attention.",
			body_text=f"""{get_formatted_error()}"""
		)
		return None


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
