"""Provides classes for bets and bet types."""

import math
from enum import Enum, unique
from fractions import Fraction
from typing import Union

from . import state as game_state


@unique
class BetOutcome(Enum):
    """Represents the outcome of a bet."""
    UNDECIDED = 0
    WIN = 1
    LOSE = 2
    TIE = 3


class Bet:
    """A view object on a type of bet.

    Args:
        state: The game state object.

    Attributes:
        code: String representing the type of the bet.
        wager: Amount of wager made on this bet. Read only.
    """

    code: str = NotImplementedError('Must be overridden in a child class')

    def __init__(self, *, state: game_state.GameState) -> None:
        self._state = state

    @property
    def wager(self) -> int:
        """Amount of wager on this bet."""
        return self._state.bets.get(BetType(self.code), 0)

    def check(self, *, roll: int) -> BetOutcome:
        """Checks the outcome of this bet after a given roll.

        Args:
            roll: Dice roll sum of the current round.

        Returns:
            The outcome of the bet.
        """
        raise NotImplementedError('Must be overridden in a child class')

    def pay_rate(self) -> Union[float, Fraction]:
        """Returns the winnnings-to-wager rate for this bet.

        Returns:
            Rate of winnings to wager for this bet.

        Raises:
            ValueError: If the internal point number is invalid for this bet.
        """
        raise NotImplementedError('Must be overridden in a child class')

    def winnings(self) -> int:
        """Returns the winnnings offered for this bet.

        Returns:
            Equal to wager * pay_rate(), floored.

        Raises:
            ValueError: If the internal point number is invalid for this bet.
        """
        return int(self.wager * self.pay_rate())

    def can_remove(self) -> bool:
        """Checks if this bet can be removed by the game rules."""
        raise NotImplementedError('Must be overridden in a child class')

    def min_wager(self) -> int:
        """Returns the minimum wager required for this bet.

        Returns:
            Minimum required wager, or 0 if there is no minimum.
            Note that a bet may be removable AND have a positive minimum, or be
            unremovable AND have no minimum.
        """
        raise NotImplementedError('Must be overridden in a child class')

    def max_wager(self) -> Union[int, float]:
        """Returns the maximum wager allowed for this bet.

        Returns:
            Maximum allowed wager, or math.inf if there is no maximum.
        """
        raise NotImplementedError('Must be overridden in a child class')


class PassBet(Bet):
    """A bet on the shooter winning."""

    code: str = 'pass'

    def check(self, *, roll: int) -> BetOutcome:
        if self._state.point is None:
            if roll in (7, 11):
                return BetOutcome.WIN
            elif roll in (2, 3, 12):
                return BetOutcome.LOSE
        else:
            if roll == self._state.point:
                return BetOutcome.WIN
            elif roll == 7:
                return BetOutcome.LOSE
        return BetOutcome.UNDECIDED

    def pay_rate(self) -> Union[float, Fraction]:
        return 1

    def can_remove(self) -> bool:
        return False

    def min_wager(self) -> int:
        # Disallow decreasing the wager
        return self.wager

    def max_wager(self) -> Union[int, float]:
        # If bet exists, disallow increase; allow add only if Come Out roll
        return self.wager or (math.inf if self._state.point is None else 0)


class DontPassBet(Bet):
    """A bet on the shooter losing."""

    code: str = 'dont_pass'

    def check(self, *, roll: int) -> BetOutcome:
        if self._state.point is None:
            if roll in (2, 3):
                return BetOutcome.WIN
            elif roll in (7, 11):
                return BetOutcome.LOSE
            elif roll == 12:
                return BetOutcome.TIE
        else:
            if roll == 7:
                return BetOutcome.WIN
            elif roll == self._state.point:
                return BetOutcome.LOSE
        return BetOutcome.UNDECIDED

    def pay_rate(self) -> Union[float, Fraction]:
        return 1

    def can_remove(self) -> bool:
        return True

    def min_wager(self) -> int:
        return 0

    def max_wager(self) -> Union[int, float]:
        # If bet exists, disallow increase; allow add only if Come Out roll
        return self.wager or (math.inf if self._state.point is None else 0)


# Maps each point number to pay rate of a Pass Odds bet
_PASS_ODDS_PAY_RATE = {
    4: Fraction(6, 3),
    5: Fraction(6, 4),
    6: Fraction(6, 5),
    8: Fraction(6, 5),
    9: Fraction(6, 4),
    10: Fraction(6, 3),
}

# Maps each point number to maximum wager rate of a Pass Odds bet
_PASS_ODDS_MAX_WAGER_RATE = {
    4: 3,
    5: 4,
    6: 5,
    8: 5,
    9: 4,
    10: 3,
}


class PassOddsBet(Bet):
    """An Odds bet on a Pass bet winning."""

    code: str = 'pass_odds'

    def check(self, *, roll: int) -> BetOutcome:
        assert self._state.point is not None, 'Point must be set for this bet'
        if roll == self._state.point:
            return BetOutcome.WIN
        elif roll == 7:
            return BetOutcome.LOSE
        return BetOutcome.UNDECIDED

    def pay_rate(self) -> Union[float, Fraction]:
        try:
            return _PASS_ODDS_PAY_RATE[self._state.point]
        except KeyError:
            raise ValueError(
                f'{self._state.point!r} is invalid point, expected one of '
                f'{", ".join(_PASS_ODDS_PAY_RATE.keys())}'
            )

    def can_remove(self) -> bool:
        return True

    def min_wager(self) -> int:
        return 0

    def max_wager(self) -> Union[int, float]:
        # Allow only if Point roll AND a Pass bet exists.
        if self._state.point is None:
            return 0
        pass_wager = self._state.bets.get(BetType.PASS, 0)
        if not pass_wager:
            return 0
        return int(pass_wager * _PASS_ODDS_MAX_WAGER_RATE[self._state.point])


class DontPassOddsBet(Bet):
    """An Odds bet on a Don't Pass bet winning."""

    code: str = 'dont_pass_odds'

    def check(self, *, roll: int) -> BetOutcome:
        assert self._state.point is not None, 'Point must be set for this bet'
        if roll == 7:
            return BetOutcome.WIN
        elif roll == self._state.point:
            return BetOutcome.LOSE
        return BetOutcome.UNDECIDED

    def pay_rate(self) -> Union[float, Fraction]:
        try:
            return 1 / _PASS_ODDS_PAY_RATE[self._state.point]
        except KeyError:
            raise ValueError(
                f'{self._state.point!r} is invalid point, expected one of '
                f'{", ".join(_PASS_ODDS_PAY_RATE.keys())}'
            )

    def can_remove(self) -> bool:
        return True

    def min_wager(self) -> int:
        return 0

    def max_wager(self) -> Union[int, float]:
        # Allow only if Point roll AND a Don't Pass bet exists.
        if self._state.point is None:
            return 0
        dont_pass_wager = self._state.bets.get(BetType.DONT_PASS, 0)
        if not dont_pass_wager:
            return 0
        pass_odds_wager_rate = _PASS_ODDS_MAX_WAGER_RATE[self._state.point]
        pass_odds_pay_rate = _PASS_ODDS_PAY_RATE[self._state.point]
        # assert pass_odds_wager_rate * pass_odds_pay_rate == 6
        return int(dont_pass_wager * pass_odds_wager_rate * pass_odds_pay_rate)


@unique
class BetType(Enum):
    """A type of bet."""
    PASS = PassBet.code
    DONT_PASS = DontPassBet.code
    PASS_ODDS = PassOddsBet.code
    DONT_PASS_ODDS = DontPassOddsBet.code

    def to_class(self) -> 'Bet':
        """Returns the bet class matching the current bet type."""
        return _BET_TYPE_TO_BET[self.value]


_BET_TYPE_TO_BET = {
    cls.code: cls for cls in (
        PassBet,
        DontPassBet,
        PassOddsBet,
        DontPassOddsBet,
    )
}


@unique
class BetFailReason(Enum):
    """Represents the cause of failure for adding, removing, or changing a bet.

    Bet outcomes that represent failure are truthy, and success is falsy."""
    SUCCESS = 0
    UNKNOWN = 1     # Bet was not processed
    INVALID_TYPE = 2
    NEGATIVE_WAGER = 3
    NOT_ENOUGH_BALANCE = 10
    CANNOT_ADD_BET = 20
    CANNOT_REMOVE_BET = 21
    WAGER_BELOW_MIN = 22    # If bet cannot be decreased
    WAGER_ABOVE_MAX = 23    # If bet cannot be increased

    def __bool__(self):
        return self != self.SUCCESS
