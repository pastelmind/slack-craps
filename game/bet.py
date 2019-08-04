"""Provides classes for bets and bet types."""

from enum import Enum, unique
from fractions import Fraction
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
        name: Human-readable name of the bet type.
        type: String representing the type of the bet.
    """

    name: str = 'Bet'
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

    def pay_rate(self, *, point: Union[int, None]) -> Union[float, Fraction]:
        """Returns the winnnings-to-wager rate for this bet.

        Args:
            point: Point number for this bet, or None if point is not set.

        Returns:
            Rate of winnings to wager for this bet.

        Raises:
            ValueError: If the roll is invalid for this bet.
        """
        raise NotImplementedError('Must be overridden in a child class')


class PassBet(Bet):
    """A bet on the shooter winning."""

    name: str = 'Pass'
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

    # pylint: disable=unused-argument
    def pay_rate(self, *, point=None) -> Union[float, Fraction]:
        return 1
    # pylint: enable=unused-argument


class DontPassBet(Bet):
    """A bet on the shooter losing."""

    name: str = "Don't Pass"
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

    # pylint: disable=unused-argument
    def pay_rate(self, *, point=None) -> Union[float, Fraction]:
        return 1
    # pylint: enable=unused-argument


# Maps each point number to pay rate of a Pass Odds bet
_PASS_ODDS_PAY_RATE = {
    4: Fraction(2, 1),
    5: Fraction(3, 2),
    6: Fraction(6, 5),
    8: Fraction(6, 5),
    9: Fraction(3, 2),
    10: Fraction(2, 1),
}


class PassOddsBet(Bet):
    """An Odds bet on a Pass bet winning."""

    name: str = "Pass Odds"
    type = BetType.PASS_ODDS

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        assert point is not None, 'Point must be set for a Pass Odds bet'
        if roll == point:
            return BetOutcome.WIN
        elif roll == 7:
            return BetOutcome.LOSE
        return BetOutcome.UNDECIDED

    def pay_rate(self, *, point: int) -> Union[float, Fraction]:
        try:
            return _PASS_ODDS_PAY_RATE[point]
        except KeyError:
            raise ValueError(
                f'{point!r} is invalid point, expected one of '
                f'{", ".join(_PASS_ODDS_PAY_RATE.keys())}'
            )


class DontPassOddsBet(Bet):
    """An Odds bet on a Don't Pass bet winning."""

    name: str = "Don't Pass Odds"
    type = BetType.DONT_PASS_ODDS

    def check(self, *, roll: int, point: Union[int, None]) -> BetOutcome:
        assert point is not None, "Point must be set for a Don't Pass Odds bet"
        if roll == 7:
            return BetOutcome.WIN
        elif roll == point:
            return BetOutcome.LOSE
        return BetOutcome.UNDECIDED

    def pay_rate(self, *, point: int) -> Union[float, Fraction]:
        try:
            return 1 / _PASS_ODDS_PAY_RATE[point]
        except KeyError:
            raise ValueError(
                f'{point!r} is invalid point, expected one of '
                f'{", ".join(_PASS_ODDS_PAY_RATE.keys())}'
            )


_BET_TYPE_TO_BET = {
    BetType.PASS: PassBet,
    BetType.DONT_PASS: DontPassBet,
    BetType.PASS_ODDS: PassOddsBet,
    BetType.DONT_PASS_ODDS: DontPassOddsBet,
}


def to_bet(bet_type: Union[BetType, str]) -> Bet:
    """Returns the bet class matching the given bet type.

    Args:
        bet_type: A BetType, or a string matching one.
    Returns:
        Matching class for the bet.
    Raises:
        ValueError: If the bet_type does not match any Bet.
    """
    if not isinstance(bet_type, BetType):
        bet_type = BetType(bet_type)
    return _BET_TYPE_TO_BET[bet_type]
