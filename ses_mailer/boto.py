import yaml
import logging
from pathlib import Path
from typing import Optional, Any, Iterable

from django.conf import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import boto3
from botocore.exceptions import ClientError



# Get a logger for this module. Django will automatically configure this
# based on the name 'rivia_soft.ses_mailer' from settings.py.
logger = logging.getLogger(__name__)

# For type hinting the in-memory attachment structure
InMemoryAttachment = dict[str, Any]


class SESv2_boto3:
	"""
	A robust and optimized class to handle sending emails using AWS SESv2.
	It supports plain text, HTML, custom headers, file attachments, and in-memory attachments.
	Errors and info are logged via Django's logging framework.
	"""

	def __init__(self, config_path: Path):
		"""
		Initializes the EmailSender by loading AWS config and creating a boto3 client.

		:param config_path: Path to the YAML configuration file.
		"""
		self.ses_client = self._create_ses_client(config_path)

	def _create_ses_client(self, config_path: Path) -> Any:
		"""Loads configuration from YAML and creates an SESv2 client."""
		try:
			with open(config_path, 'r') as f:
				config = yaml.safe_load(f)
			aws_config = config.get('AWS', {})
			aws_access_key_id = aws_config.get('ACCESS_KEY_ID')
			aws_secret_access_key = aws_config.get('SECRET_ACCESS_KEY')
			aws_region = aws_config.get('REGION')
			if not all([aws_access_key_id, aws_secret_access_key, aws_region]):
				raise ValueError("AWS config (ACCESS_KEY_ID, SECRET_ACCESS_KEY, REGION) is missing from config file.")
			
			logger.info(f"Initializing SES client in region: {aws_region}")
			return boto3.client('sesv2', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
		except FileNotFoundError as e:
			logger.error(f"Configuration file not found at '{config_path}'", exc_info=e)
		except (ValueError, KeyError) as e:
			logger.error(f"Error in configuration file: {e}", exc_info=e)
		except Exception as e:
			logger.error("An unexpected error occurred during SES client creation.", exc_info=e)
		return None

	def send_email(self, *, sender: str, to_addresses: list[str], subject: str, body_html: Optional[str] = None, body_text: Optional[str] = None, reply_to_addresses: list[str] = [], cc_addresses: list[str] = [], bcc_addresses: list[str] = [], attachment_file_paths: list[Path] = [], in_memory_attachments: list[InMemoryAttachment] = [], custom_headers: dict[str, str] = {}) -> Optional[str]:
		"""
		Constructs and sends an email, returning the message ID on success.
		- If any attachments are present, a raw MIME email is constructed.
		- Otherwise, the efficient 'Simple' message type is used.
		
		:param sender: The email address sending the email.
		:param to_addresses: A list of recipient email addresses.
		:param subject: The subject of the email.
		:param body_html: The HTML version of the email body.
		:param body_text: The plain text version of the email body.
		:param reply_to_addresses: List of email addresses for the 'Reply-To' field.
		:param cc_addresses: List of CC recipient email addresses.
		:param bcc_addresses: List of BCC recipient email addresses.
		:param attachment_file_paths: List of file paths to attach.
		:param in_memory_attachments: List of in-memory files. Each is a dict: {'content': bytes, 'filename': str}
		:param custom_headers: Dictionary of custom headers.
		:return: The MessageId of the sent email, or None if sending failed.
		"""
		if not self.ses_client:
			logger.warning("SES client is not initialized. Aborting sending email.")
			return None

		if not body_html and not body_text:
			# This is a programming error, so we still raise an exception.
			raise ValueError("Either body_html or body_text must be provided.")

		destination = {'ToAddresses': to_addresses, 'CcAddresses': cc_addresses, 'BccAddresses': bcc_addresses}

		try:
			# A raw email is required if there are any attachments.
			if attachment_file_paths or in_memory_attachments:
				msg = MIMEMultipart('mixed')
				msg['Subject'] = subject
				msg['From'] = sender
				msg['To'] = ", ".join(to_addresses)
				if cc_addresses: msg['Cc'] = ", ".join(cc_addresses)
				if reply_to_addresses: msg.add_header('Reply-To', ", ".join(reply_to_addresses))
				for key, value in custom_headers.items():
					msg.add_header(key, value)

				msg_body = MIMEMultipart('alternative')
				if body_text: msg_body.attach(MIMEText(body_text, 'plain', 'utf-8'))
				if body_html: msg_body.attach(MIMEText(body_html, 'html', 'utf-8'))
				msg.attach(msg_body)

				for file_path_str in attachment_file_paths:
					file_path = Path(file_path_str)
					try:
						with open(file_path, 'rb') as f:
							part = MIMEApplication(f.read())
							part.add_header('Content-Disposition', 'attachment', filename=file_path.name)
							msg.attach(part)
					except FileNotFoundError:
						logger.warning(f"Attachment file not found: {file_path}. Skipping.")

				for attachment in in_memory_attachments:
					try:
						part = MIMEApplication(attachment['content'])
						part.add_header('Content-Disposition', 'attachment', filename=attachment['filename'])
						msg.attach(part)
					except KeyError as e:
						logger.warning(f"In-memory attachment missing required key: {e}. Skipping.")

				response = self.ses_client.send_email(
					Destination=destination,
					Content={
						'Raw':{'Data': msg.as_string()}
					},
					FromEmailAddress=sender
				)
			else:
				# Use the efficient 'Simple' message type for emails without attachments.
				body = {}
				if body_text: body['Text'] = {'Data': body_text, 'Charset': 'UTF-8'}
				if body_html: body['Html'] = {'Data': body_html, 'Charset': 'UTF-8'}
				email_headers = [{'Name': k, 'Value': v} for k, v in custom_headers.items()]

				response = self.ses_client.send_email(
					FromEmailAddress=sender,
					Destination=destination,
					ReplyToAddresses=reply_to_addresses,
					Content={
						'Simple': {
							'Subject': {'Data': subject, 'Charset': 'UTF-8'},
							'Body': body,
							'Headers': email_headers
						}
					}
				)

			message_id = response.get('MessageId')
			logger.info(f"Email sent successfully to {', '.join(to_addresses)}. Message ID: {message_id}")
			return message_id

		except ClientError as e:
			logger.error(f"An SES error occurred: {e.response['Error']}", exc_info=e)
		except Exception as e:
			logger.exception("An unexpected error occurred while sending email.", exc_info=e)
		return None


SES_MAILER = SESv2_boto3(settings.CONFIG_FILE_PATH)
