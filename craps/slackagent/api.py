"""Provides methods for calling Slack's APIs."""

from slack import WebClient
from slack.web.classes.messages import Message

from local_settings import SLACK_OAUTH_TOKEN


_client = WebClient(SLACK_OAUTH_TOKEN)


def post_message(channel: str, message: Message):
    """Posts a message to a channel."""
    return _client.chat_postMessage(channel=channel, **message.to_dict())
