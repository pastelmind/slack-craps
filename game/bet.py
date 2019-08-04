"""Provides classes for bets and bet types."""

from enum import Enum, unique
from typing import Union


@unique
class BetType(Enum):
    """A type of bet."""
    PASS = 'pass'
    DONT_PASS = 'dont_pass'
    PASS_ODDS = 'pass_odds'
    DONT_PASS_ODDS = 'dont_pass_odds'


@unique
class BetOutcome(Enum):
    """Represents the outcome of a bet."""
    UNDECIDED = 0
    WIN = 1
    LOSE = 2
    TIE = 3


class Bet:
    """A single bet.

    Args:
        bet_type: The type of the bet.
        amount: Amount to bet.

    Attributes:
        type: String representing the type of the bet.
    """

    type: BetType = NotImplementedError('Must be overridden in a child class')

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        """Checks the outcome of this bet after a given roll.

        Args:
            roll: Dice roll sum of the current round.
            point: Point number, or None if not set.

        Returns:
            The outcome of the bet.
        """
        raise NotImplementedError('Must be overridden in a child class')


class PassBet(Bet):
    """A bet on the shooter winning."""

    type = BetType.PASS

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        if point is None:
            if roll in (7, 11):
                return BetOutcome.WIN
            elif roll in (2, 3, 12):
                return BetOutcome.LOSE
        else:
            if roll == point:
                return BetOutcome.WIN
            elif roll == 7:
                return BetOutcome.LOSE
        return BetOutcome.UNDECIDED


class DontPassBet(Bet):
    """A bet on the shooter losing."""

    type = BetType.DONT_PASS

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        if point is None:
            if roll in (2, 3):
                return BetOutcome.WIN
            elif roll in (7, 11):
                return BetOutcome.LOSE
            elif roll == 12:
                return BetOutcome.TIE
        else:
            if roll == 7:
                return BetOutcome.WIN
            elif roll == point:
                return BetOutcome.LOSE
        return BetOutcome.UNDECIDED


class PassOddsBet(Bet):
    """An Odds bet on a Pass bet winning."""

    type = BetType.PASS_ODDS

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        assert point is not None, 'Point must be set for a Pass Odds bet'
        if roll == point:
            return BetOutcome.WIN
        elif roll == 7:
            return BetOutcome.LOSE
        return BetOutcome.UNDECIDED


class DontPassOddsBet(Bet):
    """An Odds bet on a Don't Pass bet winning."""

    type = BetType.DONT_PASS_ODDS

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        assert point is not None, "Point must be set for a Don't Pass Odds bet"
        if roll == 7:
            return BetOutcome.WIN
        elif roll == point:
            return BetOutcome.LOSE
        return BetOutcome.UNDECIDED
