"""Slack bot that grabs the source of Slack posts."""

from http import HTTPStatus
from sys import stderr
from time import time
from typing import Any

import flask
from slack import WebClient

from local_settings import SLACK_OAUTH_TOKEN, SLACK_SIGNING_SECRET


def _is_valid_request(request: flask.Request) -> bool:
    """Verifies the timestamp and signature of an incoming Slack request."""
    timestamp = request.headers.get('X-Slack-Request-Timestamp')

    # If the timestamp is more than 5 minutes old, it could be a replay attack.
    # This judgement is based on:
    # - https://api.slack.com/docs/verifying-requests-from-slack#step-by-step_walk-through_for_validating_a_request
    # - https://github.com/slackapi/python-slack-events-api/blob/master/slackeventsapi/server.py
    if abs(time() - int(timestamp)) > 60 * 5:
        print('Invalid timestamp', file=stderr)
        return False

    is_valid = WebClient.validate_slack_signature(
        signing_secret=SLACK_SIGNING_SECRET,
        data=request.get_data(),
        timestamp=timestamp,
        signature=request.headers.get('X-Slack-Signature'),
    )
    if not is_valid:
        print('Invalid signature', file=stderr)
        return False

    return True


def on_request(request: flask.Request) -> Any:
    """Handles an interaction event request sent by Slack.

    Args:
        request: The Flask Request object.
            <https://flask.palletsprojects.com/en/1.0.x/api/#flask.Request>

    Returns:
        Response text or object to be passed to `make_response()`.
        <https://flask.palletsprojects.com/en/1.0.x/api/#flask.Flask.make_response>
    """
    if request.method != 'POST':
        return 'Only POST requests are accepted', HTTPStatus.METHOD_NOT_ALLOWED

    if not _is_valid_request(request):
        return '', HTTPStatus.FORBIDDEN

    if request.is_json:
        data = request.json
        data_type = data['type']

        # A request URL challenge sent by Slack--return it immediately.
        if data_type == 'url_verification':
            return data['challenge']

        raise NotImplementedError(f'Unsupported event: {data}')

    else:
        # This is probably an application/x-www-form-urlencoded format, which
        # is most likely an interaction event.
        # We're handle these later
        return '', HTTPStatus.FORBIDDEN

    return '', HTTPStatus.OK
