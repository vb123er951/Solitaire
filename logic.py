"""Core logic for the Solitaire game."""
import random
import copy
from constants import SUITS, RANKS, SUIT_COLORS, RED, BLACK, KING, ACE, UNDO_HISTORY_LIMIT


class Card:
    """Represents a single playing card."""

    def __init__(self, rank, suit, face_up=False):
        self.rank = rank
        self.suit = suit
        self.color = SUIT_COLORS[suit]
        self.face_up = face_up

    def to_dict(self):
        """Serializes the card to a dictionary."""
        return {'rank': self.rank, 'suit': self.suit, 'face_up': self.face_up}

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
        self.cards.append(card)

    def remove_card(self):
        return self.cards.pop() if self.cards else None

    def peek(self):
        return self.cards[-1] if self.cards else None

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
        if not card: return False
        if not self.cards: return card.rank == ACE
        return card.suit == self.peek().suit and card.rank == self.peek().rank + 1


class Tableau(Pile):
    """The seven tableau piles."""

    def can_add(self, card):
        if not card: return False
        if not self.cards: return card.rank == KING
        top_card = self.peek()
        return card.color != top_card.color and card.rank == top_card.rank - 1


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

    def _get_snapshot(self):
        """Creates a deep copy of the current card state."""
        return {
            'stock': copy.deepcopy(self.stock.cards),
            'waste': copy.deepcopy(self.waste.cards),
            'foundations': [copy.deepcopy(f.cards) for f in self.foundations],
            'tableaus': [copy.deepcopy(t.cards) for t in self.tableaus]
        }

    def save_state(self):
        """Saves a snapshot to history for undoing."""
        self.history.append(self._get_snapshot())
        if len(self.history) > UNDO_HISTORY_LIMIT:
            self.history.pop(0)

    def undo(self):
        """Reverts to the last saved state."""
        if not self.history: return False
        state = self.history.pop()
        self.stock.cards = state['stock']
        self.waste.cards = state['waste']
        for i, cards in enumerate(state['foundations']): self.foundations[i].cards = cards
        for i, cards in enumerate(state['tableaus']): self.tableaus[i].cards = cards
        return True

    def reset(self):
        """Initializes/Resets the game state."""
        self.history = []
        random.shuffle(self.deck)
        self.stock.cards = [copy.deepcopy(c) for c in self.deck]
        for c in self.stock.cards: c.face_up = False
        self.waste.cards = []
        for f in self.foundations: f.cards = []
        for t in self.tableaus: t.cards = []

        # Deal to tableaus
        for i in range(7):
            for j in range(i, 7):
                card = self.stock.remove_card()
                if i == j: card.face_up = True
                self.tableaus[j].add_card(card)

    def to_dict(self):
        """Serializes the entire game state to a dictionary."""
        def serialize_pile(cards): return [c.to_dict() for c in cards]
        def serialize_snapshot(s):
            return {
                'stock': serialize_pile(s['stock']),
                'waste': serialize_pile(s['waste']),
                'foundations': [serialize_pile(f) for f in s['foundations']],
                'tableaus': [serialize_pile(t) for t in s['tableaus']]
            }

        return {
            'stock': serialize_pile(self.stock.cards),
            'waste': serialize_pile(self.waste.cards),
            'foundations': [serialize_pile(f.cards) for f in self.foundations],
            'tableaus': [serialize_pile(t.cards) for t in self.tableaus],
            'history': [serialize_snapshot(h) for h in self.history]
        }

    def from_dict(self, data):
        """Restores the game state from a dictionary."""
        def deserialize_pile(cards_data): return [Card.from_dict(c) for c in cards_data]
        def deserialize_snapshot(s_data):
            return {
                'stock': deserialize_pile(s_data['stock']),
                'waste': deserialize_pile(s_data['waste']),
                'foundations': [deserialize_pile(f) for f in s_data['foundations']],
                'tableaus': [deserialize_pile(t) for t in s_data['tableaus']]
            }

        self.stock.cards = deserialize_pile(data['stock'])
        self.waste.cards = deserialize_pile(data['waste'])
        for i, f_data in enumerate(data['foundations']): self.foundations[i].cards = deserialize_pile(f_data)
        for i, t_data in enumerate(data['tableaus']): self.tableaus[i].cards = deserialize_pile(t_data)
        self.history = [deserialize_snapshot(h) for h in data.get('history', [])]

    def draw_from_stock(self):
        """Draws a card from the stock to the waste."""
        self.save_state()
        if not self.stock.cards:
            self.stock.cards = self.waste.cards[::-1]
            for card in self.stock.cards: card.face_up = False
            self.waste.cards = []
        else:
            card = self.stock.remove_card()
            card.face_up = True
            self.waste.add_card(card)

    def move_card(self, source_pile, dest_pile):
        """Attempts to move the top card from source to destination."""
        card = source_pile.peek()
        if card and dest_pile.can_add(card):
            self.save_state()
            dest_pile.add_card(source_pile.remove_card())
            if isinstance(source_pile, Tableau) and source_pile.cards:
                source_pile.peek().face_up = True
            return True
        return False

    def move_stack(self, source_tableau, dest_tableau, card):
        """Attempts to move a sub-stack starting from 'card' to dest_tableau."""
        if not (isinstance(source_tableau, Tableau) and isinstance(dest_tableau, Tableau)): return False
        try:
            index = source_tableau.cards.index(card)
        except ValueError: return False

        if card.face_up and dest_tableau.can_add(card):
            self.save_state()
            stack = source_tableau.cards[index:]
            source_tableau.cards = source_tableau.cards[:index]
            dest_tableau.cards.extend(stack)
            if source_tableau.cards: source_tableau.peek().face_up = True
            return True
        return False

    def check_win(self):
        """Checks if the game is won (all foundations are full)."""
        return all(len(f.cards) == 13 for f in self.foundations)

    def can_auto_finish(self):
        """Checks if the game can be automatically finished."""
        if self.stock.cards or self.waste.cards: return False
        return all(all(c.face_up for c in t.cards) for t in self.tableaus)
