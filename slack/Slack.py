


class Slack: 
    description: str = "Slack SDK for MCP."
    def __init__(self, slack_client_id: str, slack_client_secret: str, slack_channel_id: str, slack_bot_token: str, always_add_users: list[str]):
        self.environment_vars = {
            "slack_client_id": slack_client_id,
            "slack_client_secret": slack_client_secret,
            "slack_channel_id": slack_channel_id,
            "slack_bot_token": slack_bot_token
        }
        # users to always add to all the conversations and channels 
        self.always_add_users = always_add_users
        self.client = WebClient(token=self.environment_vars["slack_bot_token"])

    def read(self, channel_id: str, limit: int = 100):
        # return all messages the MCP server should handle which messages are new
        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            return response 
        except SlackApiError as e:
            print(f"Error: {e}")
            return []

    def check_on_going_dms(self, conversation_types: str = "im,mpim"):
        """
        Lists all active conversations 
        """
        try:
            response = self.client.conversations_list(types=conversation_types)
            return response 

        except SlackApiError as e:
            print(f"Error: {e}")
            return []

    def send_messsage(self, message: str, sending_bot_id: str, target_channel_id: str):
        try:
            response = self.client.chat_postMessage(
                channel=target_channel_id,
                text=message,
                thread_ts=sending_bot_id
            )
            return response 
        except SlackApiError as e:
            print(f"Error: {e}")
            return []

    def create_app(self):
        # apps.manifest.create()
        pass 

    def create_channel(self):
        # channels.create()
        pass 

    def open_conversation(self):
        # unlike a channel this opens a conversation with a user. 
        pass 

    def get_channel_info(self):
        # channels.info()
        pass 

    def reply(self):
        # chat.postMessage()
        pass 

    def get_user_info(self):
        # users.info()
        pass 

    def react(self):
        pass 

    def delete(self):
        # chat.delete()
        # optionally delete the chat messages 
        pass 