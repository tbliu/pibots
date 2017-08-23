from twilio.rest import Client
import auth_keys as auth
import datetime

def send_msg():
    account_sid = auth.get_twilio_sid()
    auth_token = auth.get_twilio_auth()

    client = Client(account_sid, auth_token)
    timestamp = datetime.datetime.now()
    message = client.api.account.messages.create(to=auth.get_phone_number(),\
            from_ = auth.get_twilio_number(), \
            body = "Security Alert at " + timestamp.strftime("%A %d %B %Y %I:%M:%S%p"))

