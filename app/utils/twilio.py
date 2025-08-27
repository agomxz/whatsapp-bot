from twilio.rest import Client
from app.config import TWILIO_KEY, TO_WHATSAPP, FROM_WHATSAPP, TWILIO_ACCOUNT_SID
from app.config import logger
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse


class TwilioService:
    def __init__(self):
        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_KEY)

    def send_message(self, body_message: str):
        try:
            message = self.client.messages.create(
                from_=FROM_WHATSAPP, to=TO_WHATSAPP, body=body_message
            )
            logger.info(message)

            twiml = MessagingResponse()

        except TwilioRestException as e:
            logger.error("Twilio error: %s", e)

        except Exception as e:
            logger.error("Unexpected error: %s", e)
