"""A proof-of-concept, single player Craps game in the terminal."""

from fractions import Fraction
from operator import attrgetter
from random import randint

from game.bet import BetType, BetOutcome
from game.bet import PassBet, DontPassBet
from game.state import GameState


# Multipliers on returns of a Pass Odds bet for each point number
PASS_ODDS_MULTIPLIER = {
    4: Fraction(6, 3),
    5: Fraction(6, 4),
    6: Fraction(6, 5),
    8: Fraction(6, 5),
    9: Fraction(6, 4),
    10: Fraction(6, 3),
}


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
    for bet_type in BetType:
        bet = state.get_bet(bet_type)

        assert bet.wager >= 0, 'Bet wager cannot be negative'
        if bet.wager == 0:
            if bet.can_add():
                assert bet.max_wager() > 0
                allowed_bet_types.add(bet_type)
        elif (bet.can_remove() or
              bet.min_wager() < bet.wager or bet.max_wager() > bet.wager):
            allowed_bet_types.add(bet_type)

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

        bet = state.get_bet(bet_type)
        new_wager = bet.wager + bet_amount

        if new_wager < 0:
            print("You can't bet a negative amount!")
            continue
        elif bet_amount > state.balance:
            print("You don't have that much money.")
            continue

        min_wager = bet.min_wager()
        if min_wager > new_wager:
            print(f'You have to bet at least ${min_wager}')
            continue
        max_wager = bet.max_wager()
        if max_wager < new_wager:
            print(f'You cannot bet more than ${max_wager}')
            continue

        print('You made a bet.')
        state.balance -= bet_amount
        state.bets[bet_type] = new_wager
        break


    (roll1, roll2) = state.last_roll = (randint(1, 6), randint(1, 6))
    print(f'You rolled {roll1}, {roll2}')
    roll_sum = sum(state.last_roll)

    is_game_finished = False

    # Use a list so we can modify the state.bets dictionary inside the loop
    for bet_type, wager in list(state.bets.items()):
        bet = state.get_bet(bet_type)
        bet_result = bet.check(roll=roll_sum)

        if bet_result == BetOutcome.WIN:
            win_amount = wager + bet.winnings()
            state.balance += win_amount
            print(f'  You won a {bet.name} bet! (+${win_amount})')
        elif bet_result == BetOutcome.LOSE:
            print(f'  You lost a {bet.name} bet... (${wager} gone)')
        elif bet_result == BetOutcome.TIE:
            state.balance += wager
            print(f'  You tied a {bet.name} bet. (+${wager})')

        if bet_result != BetOutcome.UNDECIDED:
            del state.bets[bet_type]
            if isinstance(bet, (PassBet, DontPassBet)):
                is_game_finished = True

    if is_game_finished:
        assert not state.bets, f'Unexpected bets remaining: \n{state.bets!r}'
        state.reset_round()
    else:
        if state.point_number is None:
            state.point_number = roll_sum
            print(f'You established a point: {state.point_number}')
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
