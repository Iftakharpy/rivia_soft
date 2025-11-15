import logging
import json
import requests

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from sns_message_validator import (
    SNSMessageValidator,
    SNSMessageType,
    InvalidMessageTypeException,
    InvalidCertURLException,
    InvalidSignatureVersionException,
    SignatureVerificationFailureException,
)


logger = logging.getLogger(__name__)
sns_message_validator = SNSMessageValidator()



@csrf_exempt
def ses_sns_webhook(request):
    """
    Handles and validates incoming webhook requests from an AWS SNS topic
    subscribed to AWS SES email events.

    This view performs the following steps:
    1. Validates the authenticity of the incoming SNS message.
    2. Handles the one-time SNS subscription confirmation.
    3. Processes different types of SES event notifications (e.g., Bounce, Complaint).
    """
    # 1. We only want to process POST requests
    if request.method != 'POST':
        logger.warning(f"Received non-POST request method: {request.method}")
        return HttpResponseBadRequest("Invalid HTTP method. Only POST is accepted.")

    # 2. Validate the message type from the header for a quick check
    try:
        message_type = request.headers.get('x-amz-sns-message-type')
        sns_message_validator.validate_message_type(message_type)
    except InvalidMessageTypeException as e:
        logger.error(f"Message type validation failed.", exc_info=e)
        return HttpResponseBadRequest("Invalid SNS message type.")

    # 3. Decode the request body and parse it as JSON
    try:
        message = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError as e:
        error_msg = 'Request body is not valid JSON.'
        logger.error(f"{error_msg}", exc_info=e)
        return HttpResponseBadRequest(error_msg)

    # 4. Perform a full cryptographic validation of the message signature
    try:
        sns_message_validator.validate_message(message=message)
    except InvalidCertURLException as e:
        logger.error(f"Message certificate URL is invalid.", exc_info=e)
        return HttpResponseBadRequest("Invalid certificate URL.")
    except InvalidSignatureVersionException as e:
        logger.error(f"Message signature version is invalid.", exc_info=e)
        return HttpResponseBadRequest("Unexpected signature version.")
    except SignatureVerificationFailureException as e:
        logger.error(f"Message signature verification failed.", exc_info=e)
        return HttpResponseBadRequest("Failed to verify message signature.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during message validation.", exc_info=e)
        return HttpResponseBadRequest("Message validation failed due to an unexpected error.")


    # --- Message Type Handling ---

    # 5. Handle the one-time subscription confirmation from AWS
    if message_type == SNSMessageType.SubscriptionConfirmation.value:
        subscribe_url = message.get('SubscribeURL')
        logger.info(f"Confirming SNS subscription by visiting: {subscribe_url}")
        try:
            resp = requests.get(subscribe_url)
            resp.raise_for_status()  # Raises an HTTPError for bad responses
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to SubscribeURL failed.", exc_info=e)
            return HttpResponse("Could not confirm subscription.", status=500)
        logger.info(f"Subscribed to {subscribe_url} successfully.")
        return HttpResponse("Subscription confirmed successfully.")

    # 6. Handle unsubscribe confirmations
    if message_type == SNSMessageType.UnsubscribeConfirmation.value:
        logger.info(f"Received UnsubscribeConfirmation for Topic: {message.get('TopicArn')}")
        return HttpResponse("Unsubscription noted.")

    # 7. This is the main logic: handle the actual SES Event Notification
    if message_type == SNSMessageType.Notification.value:
        try:
            # The SES event is a JSON string inside the 'Message' key
            ses_event_data = json.loads(message.get('Message'))
            event_type = ses_event_data.get('eventType')
            
            logger.info(f"Received SES Notification of type: {event_type}", extra=message)

            # ====================================================================
            # BUSINESS LOGIC FOR ALL SES EVENT TYPES
            # ====================================================================
            if event_type == 'Bounce':
                details = ses_event_data.get('bounce', {})
                bounce_type = details.get('bounceType')
                for recipient in details.get('bouncedRecipients', []):
                    email = recipient.get('emailAddress')
                    reason = recipient.get('diagnosticCode')
                    logger.warning(
                        f"'{bounce_type}' bounce for recipient: {email}. Reason: {reason}"
                    )
                    # YOUR LOGIC: If 'Permanent', add to a suppression list.

            elif event_type == 'Complaint':
                details = ses_event_data.get('complaint', {})
                for recipient in details.get('complainedRecipients', []):
                    email = recipient.get('emailAddress')
                    logger.warning(f"Complaint from: {email}")
                    # YOUR LOGIC: Add to a suppression list immediately.
            
            elif event_type == 'Delivery':
                details = ses_event_data.get('delivery', {})
                logger.info(f"Email delivered to: {details.get('recipients')}")
                # YOUR LOGIC: Mark email as 'delivered' in your database.

            elif event_type == 'Send':
                message_id = ses_event_data.get('mail', {}).get('messageId')
                logger.info(f"SES accepted email for sending. Message ID: {message_id}")
                # YOUR LOGIC: Log the messageId for tracking.

            elif event_type == 'Reject':
                reason = ses_event_data.get('reject', {}).get('reason')
                message_id = ses_event_data.get('mail', {}).get('messageId')
                logger.error(f"SES rejected email {message_id}. Reason: {reason}")
                # YOUR LOGIC: Investigate the reason for rejection.

            elif event_type == 'Open':
                message_id = ses_event_data.get('mail', {}).get('messageId')
                logger.info(f"Email opened. Message ID: {message_id}")
                # YOUR LOGIC: Update analytics for user engagement.

            elif event_type == 'Click':
                details = ses_event_data.get('click', {})
                link = details.get('link')
                message_id = ses_event_data.get('mail', {}).get('messageId')
                logger.info(f"Link clicked in email {message_id}. Link: {link}")
                # YOUR LOGIC: Update analytics for link performance.

            elif event_type == 'Rendering Failure':
                details = ses_event_data.get('failure', {})
                template = details.get('templateName')
                error = details.get('errorMessage')
                logger.critical(f"Template rendering failed for '{template}'. Error: {error}")
                # YOUR LOGIC: Alert developers to fix the email template.
            
            elif event_type == 'DeliveryDelay':
                details = ses_event_data.get('deliveryDelay', {})
                delay_type = details.get('delayType')
                recipients = details.get('delayedRecipients', [])
                logger.warning(f"Delivery delay ({delay_type}) for recipients: {recipients}")
                # YOUR LOGIC: Monitor if delays are frequent, but usually no action is needed.

            elif event_type == 'Subscription':
                details = ses_event_data.get('subscription', {})
                contact_list = details.get('contactListName')
                logger.info(f"Subscription preferences updated for contact list: {contact_list}")
                # YOUR LOGIC: Update user's subscription settings in your database.

            else:
                logger.error(f"Received an unknown or unhandled SES event type: '{event_type}'", extra=ses_event_data)
            # ====================================================================

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SES event from 'Message' key: {e}", exc_info=e)
            return HttpResponseBadRequest("Invalid JSON in SES Message.")
        
        return HttpResponse("Notification received and processed.")

    # Fallback for any other valid but unhandled message types
    logger.warning(f"Received unhandled SNS message type: {message_type}")
    return HttpResponse("Message received, but no action was taken for this type.")
