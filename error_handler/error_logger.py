import sys
import traceback
from datetime import datetime, timezone
from django.conf import settings


def log_server_error_to_file(e=None):
  # Get exception details
  type_, value, tb = sys.exc_info()
  formatted_traceback = "".join(traceback.format_exception(type_, value, tb))

  # Get current timestamp in UTC format
  timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # ISO 8601 format

  # Write the error details to the log file
  with open(settings.ERROR_LOG_FILE_PATH, 'a+') as f:
    f.write(f"[{timestamp} UTC] {type_.__name__}: {value}\n")
    f.write(f"{'='*35}\n")
    f.write(formatted_traceback)
    f.write(f"{'='*35}\n")
    f.write(f"\n\n\n")
  