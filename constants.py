"""Constants for the Solitaire game."""

# Suits
HEARTS = 'Hearts'
DIAMONDS = 'Diamonds'
CLUBS = 'Clubs'
SPADES = 'Spades'

SUITS = [HEARTS, DIAMONDS, CLUBS, SPADES]

# Colors
RED = 'Red'
BLACK = 'Black'

SUIT_COLORS = {
    HEARTS: RED,
    DIAMONDS: RED,
    CLUBS: BLACK,
    SPADES: BLACK
}

# Ranks
ACE = 1
JACK = 11
QUEEN = 12
KING = 13

RANKS = list(range(1, 14))

RANK_NAMES = {
    ACE: 'A',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: '10',
    JACK: 'J',
    QUEEN: 'Q',
    KING: 'K'
}
