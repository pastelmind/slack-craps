"""Provides classes for bets and bet types."""

from enum import Enum, unique


@unique
class BetType(Enum):
    """Represents a type of bet."""
    PASS = 'pass'
    DONT_PASS = 'dont_pass'
    PASS_ODDS = 'pass_odds'
    DONT_PASS_ODDS = 'dont_pass_odds'


# TODO Actually make this useful, or remove it
class Bet:
    """Represents a single bet.

    Args:
        bet_type: The type of the bet.
        amount: Amount to bet.
    """

    def __init__(self, bet_type: BetType, amount: int) -> None:
        self.type = bet_type
        self.amount = amount
