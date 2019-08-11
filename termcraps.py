"""A proof-of-concept, single player Craps game in the terminal."""

from operator import attrgetter

from game.bet import BetType, BetOutcome
from game.state import GameState, RollOutcome


def round(state: GameState) -> None:
    """A single round (die roll stage) in a round of craps."""

    state.round += 1
    if state.point is None:
        print(f'Round {state.round}: Come Out phase')
    else:
        print(f'Round {state.round}: Point phase (point: {state.point})')

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
            if state.point is None:
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

    bet_outcomes = state.shoot_dice()
    (roll1, roll2) = state.last_roll
    print(f'You rolled {roll1}, {roll2}')

    for bet_type, outcome, wager, winnings in bet_outcomes:
        bet_class = bet_type.to_class()
        bet_name = bet_class.name

        if outcome == BetOutcome.WIN:
            print(f'  You won a {bet_name} bet! (+${winnings})')
        elif outcome == BetOutcome.LOSE:
            print(f'  You lost a {bet_name} bet... (${wager} gone)')
        elif outcome == BetOutcome.TIE:
            print(f'  You tied a {bet_name} bet. (+${winnings})')

    roll_outcome = state.last_roll_outcome
    if roll_outcome == RollOutcome.FINISHED:
        print('Round finished.')
    elif roll_outcome == RollOutcome.POINT_ESTABLISHED:
        print(f'You established a point: {state.point}')
    else:   # Undecided
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
