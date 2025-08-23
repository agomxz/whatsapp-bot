from app.config import TWILIO_KEY
from twilio.rest import Client as twilio_client
from app.config import logger


def send_message(body_message: str ):    
    account_sid = 'AC89a4f161a470135a4c8267f35f85d120'
    auth_token = TWILIO_KEY
    client = twilio_client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        #content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
        #content_variables='{"1":"hola","2":"mensaje"}',
        to='whatsapp:+5215579123590',
        body=body_message
    )

    print(message.sid)
    
    return True