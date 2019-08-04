"""Provides classes for storing and querying the game state."""

from typing import Dict, Optional, Tuple, Union

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

    def get_bet(self, bet_type: Union['bet.BetType', str]) -> 'bet.Bet':
        """Retrieves a bet entry made by the player.

        A bet that has not been added yet will have a wager of 0.

        Args:
            bet_type: A BetType, or a string matching one.

        Returns:
            A matching bet entry.

        Raises:
            ValueError: If the bet type does not match any Bet.
        """
        if not isinstance(bet_type, bet.BetType):
            bet_type = bet.BetType(bet_type)
        bet_class = bet_type.to_class()
        return bet_class(
            wager=self.bets.get(bet_type, 0),
            point=self.point_number,
            state=self,
        )
