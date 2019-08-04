"""Provides classes for storing and querying the game state."""

from typing import Dict, Optional, Tuple

from . import bet


class GameState:
    """Represents the collective state of a game.

    Args:
        balance: Starting balance of the player.
    """

    def __init__(self, balance: int) -> None:
        self.balance = balance
        self.round: int = 0
        self.point_number: Optional[int] = None
        self.bets: Dict[bet.BetType, int] = {}
        self.last_roll: Optional[Tuple[int, int]] = None

    def reset_round(self) -> None:
        """Resets a round."""
        self.round = 0
        self.point_number = None
        self.bets.clear()
        self.last_roll = None