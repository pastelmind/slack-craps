# TODO Improve docstring

from random import randint
from typing import List, Optional

from agent import Agent
from bet import Bet


class GameState:
    """Represents the entirety of the game state."""

    def __init__(self) -> None:
        self.players: List[Agent] = []
        self._point: Optional[int] = None


class RoundState:
    """Represents the state of a single round of Craps.

    Args:
        point: If the round is in the Come-Out phase, this value is None.
            Otherwise (Point phase), this value is the point rolled by the
            shooter.
    """

    def __init__(self, point: Optional[int] = None) -> None:
        self._point: Optional[int] = None
        self._bets: List[Bet] = []


class Rules:
    """A set of rules enforced by a given game."""

    def get_bet_odds(self):
        pass


def roll_die(n: int = 6) -> int:
    """Returns the result of an n-sided die roll.

    Args:
        n: The number of sides of the die.

    Returns:
        A random integer between 1 and n, inclusive.
    """
    return randint(1, n)
