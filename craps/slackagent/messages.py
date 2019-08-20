"""Provides functions for building Slack message objects."""

from typing import Iterable, Dict

from slack.web.classes.blocks import ActionsBlock
from slack.web.classes.blocks import DividerBlock
from slack.web.classes.blocks import SectionBlock
from slack.web.classes.elements import ButtonElement
from slack.web.classes.elements import ImageElement
from slack.web.classes.messages import Message

from local_settings import IMAGE_URL_BASE


def welcome_message() -> Message:
    """Builds a new welcome message object.

    Returns:
        The message object.
    """
    welcome = SectionBlock(
        text='Welcome to Slack Craps! '
        'To play a new game, message me with the word "new".'
        '\n\n_Icons made by '
        '<https://www.flaticon.com/authors/smashicons|Smashicons>'
        ' from <www.flaticon.com>, licensed under '
        '<http://creativecommons.org/licenses/by/3.0/|CC 3.0 BY>_',
        accessory=ImageElement(
            image_url=IMAGE_URL_BASE + 'dice.png',
            alt_text='Slack Craps',
        ),
    )
    return Message(blocks=[welcome], text=welcome.text)


def new_game_message(
        balance: int,
        actions: Iterable[Dict[str, str]],
        state: str,
) -> Message:
    """Builds an interactive message for a new game.

    Args:
        balance: Starting balance of the player.
        actions: List of dicts for each button. Each dict must have the 'text'
            and 'action_id' properties.
        state: An encoded string that will be included in the message.

    Returns:
        The message object.
    """
    preview_text = (
        f'New game\n'
        f'You have ${balance}.\n'
        f'You approach a Craps table...\n'
    )

    header = SectionBlock(text='New Game\n\nYou approach a Craps table.')
    status = SectionBlock(text=f'You have: ${balance}')

    buttons = []
    for action in actions:
        action.setdefault('value', '0')
        buttons.append(ButtonElement(**action))
    # Store the state string in the first button
    # use a dict to send state
    state_button = buttons[0].to_dict()
    state_button['value'] = state
    buttons[0] = state_button
    actions_block = ActionsBlock(elements=buttons)

    return Message(
        text=preview_text,
        blocks=[
            header,
            DividerBlock(),
            status,
            DividerBlock(),
            actions_block,
        ],
    )
