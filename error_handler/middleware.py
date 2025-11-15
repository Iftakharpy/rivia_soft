import sys
import logging
import uuid
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, HttpResponseServerError
from django.views.debug import ExceptionReporter
from .error_reporting import save_exception_report


# Get the logger configured in settings.py under the name 'template_errors'.
# This logger will be used for all middleware-related error logging.
logger = logging.getLogger('django')


class CustomErrorLoggingMiddleware:
    """
    A middleware that captures and logs both unhandled exceptions
    (like 5xx errors and specific 4xx exceptions) and 4xx responses returned
    directly from views.

    It acts as the final safety net for the entire application. If an error
    occurs even within a custom error handler (e.g., handler500), this
    middleware's __call__ method will catch it and generate a report.
    """
    def __init__(self, get_response):
        """
        One-time configuration and initialization.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        The main middleware entry point. This wraps the entire request-response
        cycle to act as the ultimate failsafe.
        """
        try:
            # The main request-response cycle. This will execute the view
            # and any subsequent Django processing.
            response = self.get_response(request)

            # --- PART 1: CATCHING 4XX RESPONSES ---
            # After the view has run, inspect the final response status code.
            # This catches errors returned directly by views (e.g., HttpResponseBadRequest).
            if 400 <= response.status_code < 500 and response.status_code != 404:
                logger.warning(
                    f"Client Error Response: Status {response.status_code} for path '{request.path}'. "
                    f"User: {request.user}. Method: {request.method}."
                )
            
            return response
            
        except Exception as exception:
            # This block executes ONLY if an unhandled exception escapes the
            # entire Django stack, which typically means an error occurred
            # within Django's own error handling (e.g., a broken handler500 view).
            logger.critical(
                "!!! ULTIMATE SAFETY NET TRIGGERED !!! An unhandled exception "
                "escaped the entire Django stack. This likely means the handler500 "
                "view is broken. Generating a final HTML report.",
                exc_info=False # The report itself will contain the full traceback.
            )
            
            # Use our helper to save a detailed report of this "meta-error".
            save_exception_report(request, exception)

            # Return a generic, hardcoded 500 response to the user.
            # It's critical NOT to try rendering a template here.
            return HttpResponseServerError(
                "<h1>Server Error (500)</h1><p>A critical internal error has occurred likely in error handlers.</p>",
                content_type="text/html"
            )

    def process_exception(self, request, exception):
        """
        This method is called by Django when a view raises an unhandled exception,
        before it resolves to a response or tries to call an error handler.
        """
        # A) Handle specific 4xx exceptions we don't want to create full reports for.
        if isinstance(exception, Http404):
            # Let Django proceed to the handler404 view without logging.
            return None

        if isinstance(exception, PermissionDenied):
            logger.warning(
                f"Permission Denied (403): User '{request.user}' tried to access "
                f"'{request.path}' without permission.",
                exc_info=False
            )
            # Let Django proceed to the handler403 view.
            return None
        
        if isinstance(exception, SuspiciousOperation):
            logger.error(
                f"Suspicious Operation (400): {exception}. Request path: {request.path}",
                exc_info=True
            )
            # Let Django proceed to the handler400 view.
            return None

        # B) Handle all other exceptions (these are 5xx Server Errors).
        # This logs the *original* error from the view.
        save_exception_report(request, exception)
        
        # VERY IMPORTANT: Return None to allow Django's default exception handling
        # to continue. This will trigger Django to call the appropriate handler500 view.
        # If that handler fails, the __call__ method's safety net will catch it.
        return None
