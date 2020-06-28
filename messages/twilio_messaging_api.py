import math
from twilio.rest import Client

from messages.messaging_api import MessagingAPI
from utils import load_json_file

# load credentials from file
creds = load_json_file("credentials/twilio_creds.json")

account_sid = creds["TWILIO_ACCOUNT_SID"]
auth_token = creds["TWILIO_AUTH_TOKEN"]

TWILIO_PHONE_NUMBER = creds["TWILIO_PHONE_NUMBER"]
TWILIO_PHONE_NUMBER_SID = creds["TWILIO_PHONE_NUMBER_SID"]

class TwilioMessagingAPI(MessagingAPI):

    def __init__(self, webhook_url):
        super().__init__(webhook_url)
    
    def get_client(self):
        return Client(account_sid, auth_token)

    def send_message(self, message, person):
        """ Sends a message via SMS. If the message is too long then it sends multiple messages. """

        # filter out edge cases
        if not isinstance(message, str) or message == "":
            return

        phone_number = person.get("phone_number")
        if phone_number:
            message = self._replace_message_tokens(message, person)
            print(f"Sending the following Twilio message to {person.get('first_name')} {person.get('last_name')} ({phone_number}): {message}")

            # maximum number of characters in a twilio SMS is 1600
            twilio_max_length = 1599

            # break the message up into this many partitions if it is too long
            num_partitions = math.ceil(len(message)/twilio_max_length)

            # break up the message
            truncated_messages = []
            for _ in range(num_partitions):
                # truncate the message to the max allowed length
                try:
                    message_part = message[:twilio_max_length]
                except IndexError:
                    message_part = message
                truncated_messages.append(message_part)

                # remove the added message data from the rest of the message
                message = message[twilio_max_length:]

            for truncated_message in truncated_messages:

                self.get_client().messages.create(
                    to=phone_number,
                    from_=TWILIO_PHONE_NUMBER,
                    body=truncated_message
                )
    
    def update_webhook(self, webhook_url):
        """ update the Twilio API to call the specified URL when recieving messages """
        return self.get_twilio_phones()[TWILIO_PHONE_NUMBER].update(sms_url=f"{webhook_url}")

    def get_twilio_phones(self):
        phone_numbers = {}
        twilio_phone_list = self.get_twilio_phones_as_list()

        # map Twilio phone objects to their phone numbers so it's easy to fetch the right one
        # numbers are in the format '+1NNNDDDNNNN' where N and D are digits
        for twilio_phone_object in twilio_phone_list:
            phone_numbers[twilio_phone_object.phone_number] = twilio_phone_object

        return phone_numbers

    def get_twilio_phones_as_list(self, limit=20):
        return self.get_client().incoming_phone_numbers.list(limit=limit)

if __name__ == "__main__":
    from utils.ngrok import Ngrok
    message = "skoop de poop"

    people = [{
        "phone_number": "+18148826619",
        "first_name": "John",
        "last_name": "Schultz",
    }, {
        "phone_number": "+19145198683",
        "first_name": "Kris",
        "last_name": "Brethower",
    }]

    ng = Ngrok()
    ng.init()
    webhook = f"{ng.public_url}/sms"
    messaging_api = TwilioMessagingAPI(webhook)
    print(f"HTTP tunnel via Ngrok at: {webhook}")
    from pprint import pprint
    pprint(vars(messaging_api))   

    for person in people:
        messaging_api.send_message(message, person)
