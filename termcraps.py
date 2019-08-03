"""A proof-of-concept, single player Craps game in the terminal."""

from enum import Enum, unique
from fractions import Fraction
from operator import attrgetter
from random import randint
from typing import Dict, Optional, Tuple


@unique
class BetType(Enum):
    """Represents a type of bet."""
    PASS = 'pass'
    DONT_PASS = 'dont_pass'
    PASS_ODDS = 'pass_odds'
    DONT_PASS_ODDS = 'dont_pass_odds'


# Multipliers on returns of a Pass Odds bet for each point number
PASS_ODDS_MULTIPLIER = {
    4: Fraction(6, 3),
    5: Fraction(6, 4),
    6: Fraction(6, 5),
    8: Fraction(6, 5),
    9: Fraction(6, 4),
    10: Fraction(6, 3),
}


class Bet:
    """Represents a single bet.

    Args:
        bet_type: The type of the bet.
        amount: Amount to bet.
    """

    def __init__(self, bet_type: BetType, amount: int) -> None:
        self.type = bet_type
        self.amount = amount


class GameState:
    """Represents the collective state of a game.

    Args:
        balance: Starting balance of the player.
    """

    def __init__(self, balance: int) -> None:
        self.balance = balance
        self.round: int = 0
        self.point_number: Optional[int] = None
        self.bets: Dict[BetType, int] = {}
        self.last_roll: Optional[Tuple[int, int]] = None

    def reset_round(self) -> None:
        """Resets a round."""
        self.round = 0
        self.point_number = None
        self.bets.clear()
        self.last_roll = None


def round(state: GameState) -> None:
    """A single round (die roll stage) in a round of craps."""

    state.round += 1
    if state.point_number is None:
        print(f'Round {state.round}: Come Out phase')
    else:
        print(f'Round {state.round}: Point phase (point: {state.point_number})')

    bet_state_message = 'Your bets:'
    if state.bets:
        for bet_type, amount in state.bets.items():
            bet_state_message += f'\n  {bet_type.value}: {amount}'
    else:
        bet_state_message += '\n  None'
    print(bet_state_message)

    allowed_bet_types = set()
    if state.point_number is None:
        allowed_bet_types = {
            BetType.PASS,
            BetType.DONT_PASS,
        }
    else:
        if state.bets.get(BetType.PASS, 0):
            allowed_bet_types.add(BetType.PASS_ODDS)
        if state.bets.get(BetType.DONT_PASS, 0):
            allowed_bet_types.add(BetType.DONT_PASS_ODDS)

    assert allowed_bet_types, 'You cannot bet on anything! WTF?'

    while True:
        bet_types_str = ', '.join(map(attrgetter('value'), allowed_bet_types))
        bet_type_str = input(f'Choose bet type ({bet_types_str}): ').strip()

        if not bet_type_str:
            if state.point_number is None:
                print("You can't skip a bet in the Come Out round when you are the shooter.")
                continue
            else:
                print('You decide to skip this round.')
                break

        try:
            bet_type = BetType(bet_type_str)
        except ValueError:
            print(f'{bet_type_str!r} is not a valid bet type.')
            continue

        bet_amount_str = input(
            f'Choose amount to bet (your balance: {state.balance}) : '
        )
        try:
            bet_amount = int(bet_amount_str)
        except ValueError:
            print(f'{bet_amount_str!r} is not a valid bet amount.')
            continue

        if bet_amount < 0:
            print("You can't bet a negative amount!")
            continue
        elif bet_amount > state.balance:
            print("You don't have that much money.")
            continue

        print('You made a bet.')
        state.balance -= bet_amount
        state.bets[bet_type] = state.bets.get(bet_type, 0) + bet_amount
        break


    (roll1, roll2) = state.last_roll = (randint(1, 6), randint(1, 6))
    print(f'You rolled {roll1}, {roll2}')
    roll_sum = sum(state.last_roll)

    if state.point_number is None:
        if roll_sum in (7, 11):
            bet_amount = state.bets.pop(BetType.PASS, 0)
            if bet_amount:
                win_amount = 2 * bet_amount
                state.balance += win_amount
                print(f'You won a Pass bet! (+{win_amount})')

            bet_amount = state.bets.pop(BetType.DONT_PASS, 0)
            if bet_amount:
                print(f"You lost a Don't Pass bet! ({bet_amount} gone)")

            assert not state.bets, f'Unexpected bets remaining: \n{state.bets!r}'
            state.reset_round()

        elif roll_sum in (2, 3, 12):
            bet_amount = state.bets.pop(BetType.PASS, 0)
            if bet_amount:
                print(f'You lost a Pass bet! ({bet_amount} gone)')

            bet_amount = state.bets.pop(BetType.DONT_PASS, 0)
            if bet_amount:
                if roll_sum == 12:
                    print(f"You tied a Don't Pass bet. (+{bet_amount})")
                    state.balance += bet_amount
                else:
                    win_amount = 2 * bet_amount
                    state.balance += win_amount
                    print(f"You won a Don't Pass bet! (+{win_amount})")

            assert not state.bets, f'Unexpected bets remaining: \n{state.bets!r}'
            state.reset_round()

        else:
            state.point_number = roll_sum
            print(f'You established a point: {state.point_number}')

    else:
        if roll_sum == state.point_number:
            bet_amount = state.bets.pop(BetType.PASS, 0)
            if bet_amount:
                win_amount = 2 * bet_amount
                state.balance += win_amount
                print(f'You won a Pass bet! (+{win_amount})')

            bet_amount = state.bets.pop(BetType.PASS_ODDS, 0)
            if bet_amount:
                win_multiplier = 1 + PASS_ODDS_MULTIPLIER[state.point_number]
                win_amount = int(win_multiplier * bet_amount)
                state.balance += win_amount
                print(f'You won a Pass Odds bet! (+{win_amount})')

            bet_amount = state.bets.pop(BetType.DONT_PASS, 0)
            if bet_amount:
                print(f"You lost a Don't Pass bet! ({bet_amount} gone)")

            bet_amount = state.bets.pop(BetType.DONT_PASS_ODDS, 0)
            if bet_amount:
                print(f"You lost a Don't Pass Odds bet! ({bet_amount} gone)")

            assert not state.bets, f'Unexpected bets remaining: \n{state.bets!r}'
            state.reset_round()

        elif roll_sum == 7:
            bet_amount = state.bets.pop(BetType.PASS, 0)
            if bet_amount:
                print(f'You lost a Pass bet! ({bet_amount} gone)')

            bet_amount = state.bets.pop(BetType.PASS_ODDS, 0)
            if bet_amount:
                print(f'You lost a Pass Odds bet! ({bet_amount} gone)')

            bet_amount = state.bets.pop(BetType.DONT_PASS, 0)
            if bet_amount:
                win_amount = 2 * bet_amount
                state.balance += win_amount
                print(f"You won a Don't Pass bet! (+{win_amount})")

            bet_amount = state.bets.pop(BetType.DONT_PASS_ODDS, 0)
            if bet_amount:
                win_multiplier = 1 + 1 / PASS_ODDS_MULTIPLIER[state.point_number]
                win_amount = int(win_multiplier * bet_amount)
                state.balance += win_amount
                print(f"You won a Don't Pass Odds bet! (+{win_amount})")

            assert not state.bets, f'Unexpected bets remaining: \n{state.bets!r}'
            state.reset_round()

        else:
            print('Roll it again, baby.')


def game() -> None:
    """Represents a single game of craps."""
    print('Welcome to craps!')

    balance = 1000
    state = GameState(balance)
    print(f'You start with ${balance}')

    print('-' * 32)
    while True:
        if state.balance <= 0 and not state.bets:
            print("You're broke! Game over.")
            break
        round(state)
        print('-' * 32)


if __name__ == '__main__':
    game()
