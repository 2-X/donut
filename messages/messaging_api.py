from utils import load_json_file


class MessagingAPI:

    def __init__(self, webhook_url):
        self.update_webhook(webhook_url)
    
    def quit(self):
        self.remove_webook()

    def raise_unimplemented(self):
        # TODO - dynamically say which class and which method isn't implemented
        # (e.g. "The subclass FacebookMessagingService does not implement the `send_message()` method!")
        raise Exception("The subcless ____ does not implement the ____ method!")

    def send_message(self, message):
        self.raise_unimplemented()
    
    def _replace_message_tokens(self, message, person):
        for key, value in person.items():
            message = message.replace(f"${key}$", str(value) or f"[{key}]")
        return message    
    
    def update_webhook(self, webhook_url):
        self.raise_unimplemented()
    
    def remove_webook(self):
        self.raise_unimplemented()    
