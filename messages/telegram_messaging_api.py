import requests
import urllib.parse

from messages.messaging_api import MessagingAPI
from staff.nu_crushes_staff import nu_crushes_staff

nu_crushes_bot_token = "990689994:AAEBAnRnlsjkhXtnZZkSLicVNgwtfL1X6oA"
bot_url = "t.me/nu_crushes_bot"


class TelegramMessagingAPI(MessagingAPI):

    def send_message(self, message, person):
        telegram_chat_id = person.get("telegram_chat_id")
        if telegram_chat_id:
            message = self._replace_message_tokens(message, person)
            print(f"Sending the following Telegram message to {person.get('first_name')} {person.get('last_name')} ({telegram_chat_id}): {message}".encode("utf-8"))
            send_text = (
                f"https://api.telegram.org/bot{nu_crushes_bot_token}/"
                f"sendMessage?chat_id={telegram_chat_id}"
                f"&parse_mode=Markdown&text={urllib.parse.quote(self._escape_telegram(message))}"
            )
            response = requests.get(send_text)
            jsonified_response = response.json()
            if jsonified_response.get("ok") == False:
                print(f"ERROR SENDING TELEGRAM MESSAGE {jsonified_response}")
            return jsonified_response

    def send_message_to_all_admins(self, message):
        print(f"Sending the following Telegram message to all admins: {message}".encode("utf-8"))
        for admin in nu_crushes_staff.get_admins():
            self.send_message(message, admin)
    
    def send_message_to_all_moderators(self, message):
        print(f"Sending the following Telegram message to all moderators: {message}".encode("utf-8"))
        for moderator in nu_crushes_staff.get_moderators():
            self.send_message(message, moderator)
    
    def update_webhook(self, webhook_url):
        url = f"https://api.telegram.org/bot{nu_crushes_bot_token}/setWebhook?url={webhook_url}"
        response = requests.get(url)
        return response.json()

    def remove_webhook(self):
        url = f"https://api.telegram.org/bot{nu_crushes_bot_token}/deleteWebhook"
        response = requests.get(url)
        return response.json()
    
    def _escape_telegram(self, message):
        escape_chars = ["`", "_", "*", "["]
        for char in escape_chars:
            message = message.replace(char, f"\\{char}")
        return message
