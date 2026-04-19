"""Core logic for the Solitaire game."""
import random
import copy
from constants import SUITS, RANKS, SUIT_COLORS, RED, BLACK, KING, ACE


class Card:
    """Represents a single playing card."""

    def __init__(self, rank, suit, face_up=False):
        self.rank = rank
        self.suit = suit
        self.color = SUIT_COLORS[suit]
        self.face_up = face_up

    def to_dict(self):
        """Serializes the card to a dictionary."""
        return {
            'rank': self.rank,
            'suit': self.suit,
            'face_up': self.face_up
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a card from a dictionary."""
        return cls(data['rank'], data['suit'], data['face_up'])

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


class Pile:
    """Base class for card piles."""

    def __init__(self):
        self.cards = []

    def add_card(self, card):
        """Adds a card to the pile."""
        self.cards.append(card)

    def remove_card(self):
        """Removes the top card from the pile."""
        if self.cards:
            return self.cards.pop()
        return None

    def peek(self):
        """Looks at the top card without removing it."""
        if self.cards:
            return self.cards[-1]
        return None

    def __len__(self):
        return len(self.cards)


class Stock(Pile):
    """The stock pile of face-down cards."""
    pass


class Waste(Pile):
    """The waste pile of face-up cards drawn from the stock."""
    pass


class Foundation(Pile):
    """The four foundation piles."""

    def can_add(self, card):
        """Checks if a card can be added to the foundation."""
        if not card:
            return False
        if not self.cards:
            return card.rank == ACE
        # Subsequent cards must match the suit of the pile
        if card.suit != self.peek().suit:
            return False
        return card.rank == self.peek().rank + 1


class Tableau(Pile):
    """The seven tableau piles."""

    def can_add(self, card):
        """Checks if a card can be added to the tableau."""
        if not card:
            return False
        if not self.cards:
            return card.rank == KING
        top_card = self.peek()
        return (card.color != top_card.color and
                card.rank == top_card.rank - 1)


class GameState:
    """Manages the overall game state and rules."""

    def __init__(self):
        self.deck = [Card(r, s) for s in SUITS for r in RANKS]
        self.stock = Stock()
        self.waste = Waste()
        self.foundations = [Foundation() for _ in range(4)]
        self.tableaus = [Tableau() for _ in range(7)]
        self.history = []
        self.reset()

    def save_state(self):
        """Saves a deep copy of the current state to history."""
        state = {
            'stock': copy.deepcopy(self.stock.cards),
            'waste': copy.deepcopy(self.waste.cards),
            'foundations': [copy.deepcopy(f.cards) for f in self.foundations],
            'tableaus': [copy.deepcopy(t.cards) for t in self.tableaus]
        }
        self.history.append(state)
        if len(self.history) > 50:
            self.history.pop(0)

    def undo(self):
        """Reverts to the last saved state."""
        if not self.history:
            return False
        
        state = self.history.pop()
        self.stock.cards = state['stock']
        self.waste.cards = state['waste']
        for i, cards in enumerate(state['foundations']):
            self.foundations[i].cards = cards
        for i, cards in enumerate(state['tableaus']):
            self.tableaus[i].cards = cards
        return True

    def reset(self):
        """Initializes/Resets the game state."""
        self.history = []
        random.shuffle(self.deck)
        self.stock.cards = [copy.deepcopy(c) for c in self.deck]
        for c in self.stock.cards:
            c.face_up = False
        self.waste.cards = []
        for f in self.foundations:
            f.cards = []
        for t in self.tableaus:
            t.cards = []

        # Deal to tableaus
        for i in range(7):
            for j in range(i, 7):
                card = self.stock.remove_card()
                if i == j:
                    card.face_up = True
                self.tableaus[j].add_card(card)

    def to_dict(self):
        """Serializes the entire game state to a dictionary."""
        def serialize_cards(cards):
            return [c.to_dict() for c in cards]

        def serialize_state(state):
            return {
                'stock': serialize_cards(state['stock']),
                'waste': serialize_cards(state['waste']),
                'foundations': [serialize_cards(f) for f in state['foundations']],
                'tableaus': [serialize_cards(t) for t in state['tableaus']]
            }

        return {
            'stock': serialize_cards(self.stock.cards),
            'waste': serialize_cards(self.waste.cards),
            'foundations': [serialize_cards(f.cards) for f in self.foundations],
            'tableaus': [serialize_cards(t.cards) for t in self.tableaus],
            'history': [serialize_state(h) for h in self.history]
        }

    def from_dict(self, data):
        """Restores the game state from a dictionary."""
        def deserialize_cards(cards_data):
            return [Card.from_dict(c) for c in cards_data]

        def deserialize_state(state_data):
            return {
                'stock': deserialize_cards(state_data['stock']),
                'waste': deserialize_cards(state_data['waste']),
                'foundations': [deserialize_cards(f) for f in state_data['foundations']],
                'tableaus': [deserialize_cards(t) for t in state_data['tableaus']]
            }

        self.stock.cards = deserialize_cards(data['stock'])
        self.waste.cards = deserialize_cards(data['waste'])
        for i, f_data in enumerate(data['foundations']):
            self.foundations[i].cards = deserialize_cards(f_data)
        for i, t_data in enumerate(data['tableaus']):
            self.tableaus[i].cards = deserialize_cards(t_data)
        self.history = [deserialize_state(h) for h in data.get('history', [])]

    def draw_from_stock(self):
        """Draws a card from the stock to the waste."""
        self.save_state()
        if not self.stock.cards:
            # Recycle waste back to stock
            self.stock.cards = self.waste.cards[::-1]
            for card in self.stock.cards:
                card.face_up = False
            self.waste.cards = []
        else:
            card = self.stock.remove_card()
            card.face_up = True
            self.waste.add_card(card)

    def move_card(self, source_pile, dest_pile):
        """Attempts to move the top card from source to destination."""
        card = source_pile.peek()
        if not card:
            return False

        if isinstance(dest_pile, Foundation):
            if dest_pile.can_add(card):
                self.save_state()
                dest_pile.add_card(source_pile.remove_card())
                # Flip the new top card of the source tableau
                if isinstance(source_pile, Tableau) and source_pile.cards:
                    source_pile.peek().face_up = True
                return True
        elif isinstance(dest_pile, Tableau):
            if dest_pile.can_add(card):
                self.save_state()
                dest_pile.add_card(source_pile.remove_card())
                # Flip the new top card of the source tableau if it was a tableau
                if isinstance(source_pile, Tableau) and source_pile.cards:
                    source_pile.peek().face_up = True
                return True
        return False

    def move_stack(self, source_tableau, dest_tableau, card):
        """Attempts to move a sub-stack starting from 'card' to dest_tableau."""
        if not isinstance(source_tableau, Tableau) or not isinstance(dest_tableau, Tableau):
            return False
        
        try:
            index = source_tableau.cards.index(card)
        except ValueError:
            return False

        # Can only move face-up cards
        if not card.face_up:
            return False

        if dest_tableau.can_add(card):
            self.save_state()
            stack = source_tableau.cards[index:]
            source_tableau.cards = source_tableau.cards[:index]
            dest_tableau.cards.extend(stack)
            
            # Flip the new top card of the source tableau
            if source_tableau.cards:
                source_tableau.peek().face_up = True
            return True
        return False

    def check_win(self):
        """Checks if the game is won (all foundations are full)."""
        for f in self.foundations:
            if len(f.cards) != 13:
                return False
        return True

    def can_auto_finish(self):
        """
        Checks if the game can be automatically finished.
        Condition: Stock and Waste are empty, and all Tableau cards are face-up.
        """
        if self.stock.cards or self.waste.cards:
            return False
        for tableau in self.tableaus:
            for card in tableau.cards:
                if not card.face_up:
                    return False
        return True
