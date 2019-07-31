"""Provides agent classes that represent human and computer players.

Before each die roll ("shot"), all agents are given ONE chance to make a
decision. Within a decision, an agent may add, remove, or change each type of
bet exactly ONCE. Each agent is given the following information:

- Result of previous dice roll
- Current point number (None if Come-Out stage)
- Active bets finalized up to the previous dice roll, including those that were
  won, lost, or tied by the roll.

Each agent is oblivious to the decisions made by other agents on the current
mini-round. This is intentional, as it would otherwise give an unfair advantage
to agents that make last-second decisions before the next roll.

Agents are allowed to make exactly one decision before each roll. This prevents
several potential problems, such as: a crafty agent that baits other agents to
take a favorable position later; an indecisive agent that repeatedly tweaks its
bets; or two agents fighting for the optimal position, resulting in an infinite
loop. This also applies to human agents.
"""


class Agent:
    """An abstract agent that represents a player."""

    def __init__(self, balance: int = 0) -> None:
        self._balance = balance

    def act(self) -> None:
        raise NotImplementedError('act()')


class HumanAgent(Agent):
    """An agent that interfaces with the player through Slack messages."""
    pass


class ComputerAgent(Agent):
    """An agent that represents an AI player."""
    pass
