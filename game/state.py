"""Provides classes for storing and querying the game state."""

from enum import Enum, unique
from random import randint
from typing import Dict, List, Optional, Tuple, Union

from . import bet


@unique
class RollOutcome(Enum):
    """Represents the outcome of a round after a dice roll (shoot)."""
    UNDECIDED = 0
    FINISHED = 1
    POINT_ESTABLISHED = 2


class GameState:
    """Represents the collective state of a game.

    Args:
        balance: Starting balance of the player.
    """

    def __init__(self, balance: int) -> None:
        self.balance = balance
        self.round: int = 0
        self.point: Optional[int] = None
        self.bets: Dict[bet.BetType, int] = {}
        self.last_roll: Optional[Tuple[int, int]] = None
        self.last_roll_outcome: RollOutcome = RollOutcome.UNDECIDED

    def reset_round(self) -> None:
        """Resets a round."""
        self.round = 0
        self.point = None
        self.bets.clear()

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
            point=self.point,
            state=self,
        )

    def shoot_dice(self) -> List[Tuple['bet.BetType', 'bet.BetOutcome', int]]:
        """Performs a dice shot, updates all bets, and returns their outcomes.

        If the dice roll resolves a (Don't) Pass bet, also resets the round.

        Returns:
            List of tuples of the form (BetType, BetOutcome, wager, win_amount)
            for each bet. If the bet is lost, win_amount is zero.
        """
        self.last_roll = (randint(1, 6), randint(1, 6))
        roll = sum(self.last_roll)

        is_game_finished = False
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
                if isinstance(the_bet, (bet.PassBet, bet.DontPassBet)):
                    is_game_finished = True

            results.append((bet_type, outcome, wager, winnings))

        if is_game_finished:
            assert not self.bets, f'Unexpected bets remaining: \n{self.bets!r}'
            self.reset_round()
            self.last_roll_outcome = RollOutcome.FINISHED
        elif self.point is None:
            self.point = roll
            self.last_roll_outcome = RollOutcome.POINT_ESTABLISHED
        else:
            self.last_roll_outcome = RollOutcome.UNDECIDED

        return results
