"""Provides handlers for incoming events from Slack."""

from random import randint
from sys import stderr
from typing import Any, Callable, Dict

from game.state import GameState
from .messages import new_game_message
from .messages import welcome_message
from .api import post_message


def is_event(payload: Dict[str, Any]) -> bool:
    """Checks if the given JSON payload is a Slack event.

    Args:
        payload: Dictionary representing a JSON object.

    Returns:
        True if the JSON is a Slack event, False otherwise.
    """
    try:
        return (
            payload['type'] == 'event_callback'
            and isinstance(payload['event'], dict)
        )
    except KeyError:
        return False


_event_handlers: Dict[str, Callable]


def dispatch_event(event: Dict[str, Any]) -> None:
    """Dispatches an incoming Slack event to the appropriate handler.

    Args:
        event: JSON object representing a Slack event.
    """
    event_type = event['event']['type']
    try:
        handler = _event_handlers[event_type]
    except KeyError:
        print(f'No handler found for {event_type}', file=stderr)
        return
    handler(event)


def _on_message(event: Dict[str, Any]) -> None:
    """Handles an incoming Slack event.

    Args:
        event: JSON object representing a Slack event.
    """
    channel_type = event['event']['channel_type']
    if channel_type == 'im':
        return _on_message_im(event)
    print(f'No handler found for message.{channel_type}', file=stderr)


def _on_message_im(event: Dict[str, Any]) -> None:
    """Handles an incoming Slack event.

    Args:
        event: JSON object representing a Slack event.
    """
    subtype = event['event'].get('subtype')
    if subtype:
        if subtype == 'bot_message':
            pass    # Ignore messages from this app or other apps
        # elif subtype == 'me_message':
        # elif subtype == 'message_changed':
        # elif subtype == 'message_deleted':
        # elif subtype == 'message_replied':
        # elif subtype == 'thread_broadcast':
        # elif subtype == 'ekm_access_denied':
        else:
            print(
                f'Team {event["team_id"]}: message.im Unknown subtype {subtype}'
            )
        return
    elif 'new' in event['event']['text']:
        balance = randint(20, 200) * 50
        state = GameState(balance=balance)
        actions = [
            {
                'text': "I'm sorry",
                'action_id': 'no_bets',
            },
            {
                'text': 'No bets are available yet',
                'action_id': 'no_bets_2',
            },
        ]

        message = new_game_message(
            balance=balance,
            actions=actions,
            state=state.serialize()
        )
    else:
        message = welcome_message()

    post_message(channel=event['event']['channel'], message=message)


def _on_app_home_opened(event: Dict[str, Any]) -> None:
    """Handles an incoming Slack event.

    Args:
        event: JSON object representing a Slack event.
    """
    pass


def _on_app_uninstalled(event: Dict[str, Any]) -> None:
    """Handles an incoming Slack event.

    Args:
        event: JSON object representing a Slack event.
    """
    print(f'Team {event["team_id"]}: app_uninstalled')


def _on_tokens_revoked(event: Dict[str, Any]) -> None:
    """Handles an incoming Slack event.

    Args:
        event: JSON object representing a Slack event.
    """
    tokens = event['event']['tokens']
    print(f'Team {event["team_id"]}: tokens_revoked {tokens!r}')


_event_handlers = {
    'message': _on_message,
    'app_home_opened': _on_app_home_opened,
    'app_uninstalled': _on_app_uninstalled,
    'tokens_revoked': _on_tokens_revoked,
}
