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

# --- UI & Layout Constants ---

# Colors (RGBA)
COLOR_BOARD_GREEN = (0.1, 0.3, 0.1, 1)
COLOR_OVERLAY_DARK = (0, 0, 0, 0.7)
COLOR_EMPTY_SLOT = (0.4, 0.4, 0.4, 1)

# Style Colors (RGB)
THEME_GREEN = (0.6, 0.9, 0.6)
THEME_GREEN_DOWN = (0.4, 0.7, 0.4)
THEME_RED = (0.9, 0.6, 0.6)
THEME_RED_DOWN = (0.7, 0.4, 0.4)
THEME_DEFAULT = (0.5, 0.7, 0.9)
THEME_DEFAULT_DOWN = (0.3, 0.5, 0.7)

# Dimensions & Ratios
CARD_ASPECT_RATIO = 1.5 # Height / Width

# Landscape Config
LANDSCAPE_SIDEBAR_W_RATIO = 0.16
LANDSCAPE_SIDE_MARGIN_RATIO = 0.02
LANDSCAPE_CARD_H_RATIO = 3.8 # Window.height / 3.8
LANDSCAPE_ROW_GAP_RATIO = 0.1 # card_h * 0.1
LANDSCAPE_TABLEAU_OFFSET = 0.22 # card_h * 0.22 (Standard)

# Portrait Config
PORTRAIT_SIDE_MARGIN_RATIO = 0.03
PORTRAIT_CARD_W_RATIO = 7.5 # Window.width / 7.5
PORTRAIT_ROW_GAP_RATIO = 0.4 # card_h * 0.4
PORTRAIT_TABLEAU_OFFSET = 0.22

# Common
BOTTOM_SAFE_MARGIN = 0.01 # 1% margin from bottom
UNDO_HISTORY_LIMIT = 50
