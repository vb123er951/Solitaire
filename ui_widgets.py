import os
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, ListProperty
from logic import Tableau
from constants import RANK_NAMES, RED

class CardWidget(Button):
    """Visual representation of a playing card with multi-drag and double-click."""
    
    source_pile = ObjectProperty(None)
    stack_widgets = ListProperty([])

    def __init__(self, card, source_pile, card_size=(80, 120), **kwargs):
        super().__init__(**kwargs)
        self.card = card
        self.source_pile = source_pile
        self.size_hint = (None, None)
        self.size = card_size
        # Ensure text starts at top-left
        self.bind(size=self._update_text_size)
        self.update_display()
        self.dragging = False

    def _update_text_size(self, instance, value):
        self.text_size = value

    def update_display(self):
        """Updates the card's visual appearance."""
        self.text_size = self.size # Explicitly set text_size to enable alignment
        self.border = (0, 0, 0, 0) # Remove button border for clean image display
        
        # Check for card image
        if self.card.face_up:
            image_path = f"assets/cards/{self.card.rank}_{self.card.suit}.png"
        else:
            image_path = "assets/cards/back.png"

        if os.path.exists(image_path):
            self.background_normal = image_path
            self.background_down = image_path
            self.background_disabled_normal = image_path # Keep image visible when disabled
            self.text = "" # Clear text if image exists
            self.background_color = (1, 1, 1, 1) # Opaque white to show image correctly
        else:
            # Fallback to text if image is missing
            self.background_normal = 'atlas://data/images/defaulttheme/button'
            self.background_down = 'atlas://data/images/defaulttheme/button_pressed'
            self.background_disabled_normal = 'atlas://data/images/defaulttheme/button'
            if self.card.face_up:
                suit_sym = self.card.suit[0] # H, D, C, S
                self.text = f" {RANK_NAMES[self.card.rank]}{suit_sym}"
                self.halign = 'left'
                self.valign = 'top'
                self.font_size = '18sp'
                self.bold = True
                self.color = (1, 0, 0, 1) if self.card.color == RED else (0, 0, 0, 1)
                self.background_color = (1, 1, 1, 1)
            else:
                self.text = "?"
                self.halign = 'center'
                self.valign = 'middle'
                self.font_size = '25sp'
                self.color = (1, 1, 1, 1)
                self.background_color = (0.2, 0.4, 0.6, 1)

    def on_touch_down(self, touch):
        if self.disabled:
            return False
        if self.collide_point(*touch.pos) and self.card.face_up:
            if touch.is_double_tap:
                if self.parent:
                    self.parent.auto_move(self)
                return True

            self.dragging = True
            touch.grab(self)
            
            self.stack_widgets = []
            if isinstance(self.source_pile, Tableau):
                logical_index = self.source_pile.cards.index(self.card)
                logical_stack = self.source_pile.cards[logical_index:]
                
                for card in logical_stack:
                    for w in self.parent.children:
                        if isinstance(w, CardWidget) and w.card == card and w.source_pile == self.source_pile:
                            self.stack_widgets.append(w)
                            break
            else:
                self.stack_widgets = [self]

            for w in reversed(self.stack_widgets):
                parent = w.parent
                parent.remove_widget(w)
                parent.add_widget(w)
            
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.dx
            dy = touch.dy
            for w in self.stack_widgets:
                w.x += dx
                w.y += dy
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.dragging = False
            touch.ungrab(self)
            if self.parent:
                self.parent.handle_drop(self)
            return True
        return super().on_touch_up(touch)


class PileTarget(Button):
    """A placeholder widget that acts as a drop target for a pile."""
    target_pile = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = '' # Flat color
        self.background_color = (0.4, 0.4, 0.4, 1) # Light grey for empty slots
        self.color = (1, 1, 1, 1) # White text
        self.bold = True
