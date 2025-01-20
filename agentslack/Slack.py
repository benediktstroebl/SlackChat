from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from dotenv import load_dotenv
import os
import json

load_dotenv()

class Slack: 
    name: str = "Slack SDK for MCP."
    description: str = "Slack SDK for MCP."

    def __init__(self, slack_client_id: str=None, slack_client_secret: str=None, slack_channel_id: str=None, slack_token: str=None, always_add_users: list[str]=None):
        if slack_client_id is None:
            slack_client_id = os.getenv("SLACK_CLIENT_ID")
        if slack_client_secret is None:
            slack_client_secret = os.getenv("SLACK_CLIENT_SECRET")
        if slack_channel_id is None:
            slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
        self.environment_vars = {
            "slack_client_id": slack_client_id, 
            "slack_client_secret": slack_client_secret,
            "slack_channel_id": slack_channel_id,
            "slack_token": slack_token
        }
        # users to always add to all the conversations and channels 
        self.always_add_users = always_add_users
        self.client = WebClient(token=slack_token)

    def read(self, channel_id: str, limit: int = 100):
        # return all messages the MCP server should handle which messages are new
        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            return response.data
        except SlackApiError as e:
            print(f"Error: {e}")
            return {'messages': []}

    def check_ongoing_dms(self, conversation_types: str = "im,mpim"):
        """
        Lists all active conversations 
        """
        try:
            response = self.client.conversations_list(types=conversation_types)
            return response.data

        except SlackApiError as e:
            print(f"Error: {e}")
            return {'channels': []}
        
    def get_channel_members(self, channel_id: str):
        try:
            response = self.client.conversations_members(channel=channel_id)
            return response.data
        except SlackApiError as e:
            print(f"Error: {e}")
            return {'members': []}

    def send_messsage(self, message: str, target_channel_id: str):
        try:
            response = self.client.chat_postMessage(
                channel=target_channel_id,
                text=message,
            )
            return response 
        except SlackApiError as e:
            print(f"Error: {e}")
            return {'messages': []}

    def create_app(self, app_name: str, app_description: str, manifest_path: str = "configs/app_manifest.json"):
        # sadly this is most likely an admin feature
        # you need slack premium for this. 
        manifest = self._prepare_manifest(manifest_path, app_name, app_description)
        response = self.client.apps_manifest_create(
            manifest=manifest
        )
        return response.data

    def create_channel(self, channel_name: str, is_private: bool = False):
        # channels.create()
        # registry should be updated with the channel id
        try:
            response = self.client.conversations_create(
                name=channel_name,
                is_private=is_private
            )
            return response.data
        except SlackApiError as e:
            # Check if error is due to channel already existing
            if e.response['error'] == 'name_taken':
                # Get list of channels to find the ID of the existing channel
                try:
                    response = self.client.conversations_list()
                    for channel in response['channels']:
                        if channel['name'] == channel_name:
                            return {'channel': channel}
                except SlackApiError as list_error:
                    print(f"Error listing channels: {list_error}")
                    return []
            print(f"Error: {e}")
            return []
        
    def list_channels(self):
        try:
            response = self.client.conversations_list()
            return response.data
        except SlackApiError as e:
            print(f"Error: {e}")
            return {'channels': []}
    
    def add_user_to_channel(self, channel_id: str, user_id: str):
        # channels.invite()
        try:
            response = self.client.conversations_invite(channel=channel_id, users=user_id)
            return response.data
        except SlackApiError as e:
            print(f"Error: {e}")
            return []

    def open_conversation(self, user_ids: list[str]):
        # unlike a channel this opens a conversation with a user. 
        try:
            response = self.client.conversations_open(users=user_ids + self.always_add_users)
            return response 
        
        except SlackApiError as e:
            print(f"Error: {e}")
            return []

    def get_channel_info(self):
        # channels.info()
        pass 

    
    @staticmethod
    def _prepare_manifest(manifest_path: str, app_name: str, app_description: str):
        with open(manifest_path, "r") as file:
            manifest = json.load(file)
        manifest["display_information"]["name"] = app_name
        manifest["display_information"]["description"] = app_description
        manifest["features"]["bot_user"]["display_name"] = app_name
        return manifest 

    def reply(self):
        # chat.postMessage()
        pass 

    def get_user_info(self):
        # users.info()
        pass 

    def react(self):
        pass 

    def delete_channel_history(self, channel_id: str):
        # this will again be a command line feature hopefully
        pass 

if __name__ == "__main__":

    slack = Slack(always_add_users=["U0882ARL0J2"])
    response = slack.open_conversation(["U087UDCK5D5"])
    print(json.loads(json.dumps(response.data)))
    channel_id = response['channel']['id']
    slack.send_messsage("giraffe is apologetic for the spam!", channel_id)

    resp = slack.create_channel("test3")
    channel_id = resp['channel']['id']
    slack.add_user_to_channel(channel_id, ["U087UDCK5D5", "U0882ARL0J2"])
    slack.send_messsage("giraffe is apologetic for the spam!", channel_id)
    msg = slack.read(channel_id)
    print(msg)