"""Provides Bet classes that represent the types of bets made by players."""

from typing import Optional


class Bet:
    """Abstract class that represents a bet.

    Args:
        amount: The amount of money to bet.
    """

    def __init__(self, amount: int = 0) -> None:
        self._amount = amount

    def odds_paid(self, point: Optional[int]) -> float:
        """Returns the rate of amount paid when this bet is won.

        Args:
            point: Current value of the point roll.

        Returns:
            The rate of amount paid over the amount betted.
        """
        raise NotImplementedError('odds_paid()')


class PassBet(Bet):
    """A Pass (line) bet, which wins if the shooter wins."""


class DontPassBet(Bet):
    """A Don't Pass (line) bet, which wins only if the shooter loses."""


class PassOddsBet(Bet):
    """A Pass Odds bet, which wins if the shooter hits the point."""


class DontPassOddsBet(Bet):
    """A Don't Pass Odds bet, which whins if the shooter sevens out."""
