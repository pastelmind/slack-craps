"""Provides classes for storing and querying the game state."""

from random import randint
from typing import Dict, Iterable, List, Optional, Tuple, Union

from . import bet


class YouShallNotSkipPassError(Exception):
    """Raised when the shooter didn't make a (Don't) Pass bet before the Come
    Out roll."""


class GameIsOverError(Exception):
    """Raised when an action fails because the game is already over."""


class GameState:
    """Represents the collective state of a game.

    Args:
        balance: Starting balance of the player.

    Attributes:
        is_finished: Read only. Checks if the game is over.
        round: Current round number, starts at 0. Is equal to number of dice
            rolls made so far.
    """

    def __init__(self, balance: int) -> None:
        self.balance = balance
        self.round: int = 0
        self.point: Optional[int] = None
        self.bets: Dict[bet.BetType, int] = {}
        self.last_roll: Optional[Tuple[int, int]] = None
        self._is_finished: bool = False

    @property
    def is_finished(self) -> bool:
        """Checks if the game is finished."""
        return self._is_finished

    def reset(self) -> None:
        """Resets the game state for a new game, but keeps current balance."""
        self.round = 0
        self.point = None
        self.bets.clear()
        self._is_finished = False

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
        bet_class = bet.Bet.from_type(bet_type)
        return bet_class(state=self)

    def set_bets(
            self, bets: Iterable[Tuple['bet.BetType', int]]
    ) -> List['bet.BetFailReason']:
        """Applies a series of bets to current bets and returns the results.

        Bet changes are all-or-nothing; if any bet change fails, none of them
        are applied.

        Args:
            bets: Iterable of (bet types, wager) to apply in order. Existing
                wagers are replaced by new wagers.

        Returns:
            List of reasons why each bet change failed. If all bets succeed, all
            reasons are equal to BetFailReason.SUCCESS.

        Raises:
            GameIsOverError: If the game is already over.
        """
        if self._is_finished:
            raise GameIsOverError()

        fail_reasons: List[bet.BetFailReason] = []
        old_bets = dict(self.bets)
        old_balance = self.balance

        bets_iter = iter(bets)
        for bet_type, wager in bets_iter:
            if wager < 0:
                fail_reasons.append(bet.BetFailReason.NEGATIVE_WAGER)
                break

            try:
                old_bet = self.get_bet(bet_type)
            except ValueError:
                fail_reasons.append(bet.BetFailReason.INVALID_TYPE)
                break

            self.balance += old_bet.wager - wager
            if self.balance < 0:
                fail_reasons.append(bet.BetFailReason.NOT_ENOUGH_BALANCE)
                break

            max_wager = old_bet.max_wager()
            if old_bet.wager == 0 and wager > 0 and max_wager == 0:
                fail_reasons.append(bet.BetFailReason.CANNOT_ADD_BET)
                break
            elif wager > max_wager:
                fail_reasons.append(bet.BetFailReason.WAGER_ABOVE_MAX)
                break

            if old_bet.wager > 0 and wager == 0 and not old_bet.can_remove():
                fail_reasons.append(bet.BetFailReason.CANNOT_REMOVE_BET)
                break
            elif wager < old_bet.min_wager():
                fail_reasons.append(bet.BetFailReason.WAGER_BELOW_MIN)
                break

            if wager:
                self.bets[bet_type] = wager
            else:
                self.bets.pop(bet_type, None)
            fail_reasons.append(bet.BetFailReason.SUCCESS)

        # If some bets were not applied, mark them as UNKNOWN.
        for _ in bets_iter:
            fail_reasons.append(bet.BetFailReason.UNKNOWN)

        # Undo all changes if the last reason is failure
        if fail_reasons and fail_reasons[-1]:
            self.bets = old_bets
            self.balance = old_balance

        return fail_reasons

    def shoot_dice(self) -> List[Tuple['bet.BetType', 'bet.BetOutcome', int]]:
        """Performs a dice shot, updates all bets, and returns their outcomes.

        If the dice roll is successful, also increments the round counter.
        If the dice roll resolves a (Don't) Pass bet, also ends the game.

        Returns:
            List of tuples of the form (BetType, BetOutcome, wager, win_amount)
            for each bet. If the bet is lost, win_amount is zero.

        Raises:
            GameIsOverError: If the game is already over.
            YouShallNotSkipPassError: If the shooter has not made a (Don't) Pass
                bet before the Come Out roll.
        """
        if self._is_finished:
            raise GameIsOverError()

        if self.point is None:
            if (bet.BetType.PASS not in self.bets
                    and bet.BetType.DONT_PASS not in self.bets):
                raise YouShallNotSkipPassError()

        self.last_roll = (randint(1, 6), randint(1, 6))
        roll = sum(self.last_roll)

        results = []
        # Use a tuple so we can modify the bets dict inside the loop
        for bet_type, wager in tuple(self.bets.items()):
            the_bet = self.get_bet(bet_type)
            outcome = the_bet.check(roll=roll)

            if outcome == bet.BetOutcome.WIN:
                winnings = wager + the_bet.winnings()
            elif outcome == bet.BetOutcome.TIE:
                winnings = wager
            else:   # Undecided or tied
                winnings = 0

            if outcome != bet.BetOutcome.UNDECIDED:
                self.balance += winnings
                del self.bets[bet_type]

            results.append((bet_type, outcome, wager, winnings))

        # Create a dummy pass bet to check game end conditions
        dummy_pass_bet = bet.PassBet(state=self)
        if dummy_pass_bet.check(roll=roll) != bet.BetOutcome.UNDECIDED:
            assert not self.bets, f'Unexpected bets remaining: \n{self.bets!r}'
            self._is_finished = True
        elif self.point is None:
            self.point = roll

        self.round += 1
        return results
