"""Kivy UI for the Solitaire game with Polished Drag-Drop."""

import os
import sys

# Fix for Android "Permission Denied" when copying logo/config
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.config import Config
# Set initial window size before other Kivy imports
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '780')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from logic import GameState
from storage import StorageManager
from logger import LogManager
from ui_widgets import CardWidget, PileTarget
from ui_dialogs import DialogMixin
from ui_mixins import BaseUIMixin, GameActionMixin

class GameLayout(FloatLayout, BaseUIMixin, GameActionMixin, DialogMixin):
    """Main layout for the Solitaire game."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Start logging as early as possible
        LogManager.start()
        
        # Add a dark green background
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.1, 0.3, 0.1, 1) # Dark Green Board
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        Window.bind(size=self._update_bg)

        self.game = GameState()
        self.targets = [] # List of (widget, logical_pile)
        self.auto_finish_prompted = False
        self.auto_finish_confirmed = False
        self.auto_finish_asking = False
        self.auto_finish_active = False
        self.new_game_asking = False
        self.exit_asking = False
        self.load_strings()
        Window.bind(on_resize=self.on_window_resize)
        Window.bind(on_keyboard=self.on_key)
        # Delay first render and auto-load until window and app are ready
        Clock.schedule_once(self.start_game)

    def on_key(self, window, keycode, *args):
        """Handles the physical Back button (keycode 27) on Android."""
        if keycode == 27:
            # If no other dialog is open, show exit confirmation
            if not (self.auto_finish_asking or self.new_game_asking or self.exit_asking or self.game.check_win()):
                self.confirm_exit(None)
                return True # Consume the back button event
        return False

    def _update_bg(self, instance, value):
        self.bg_rect.size = value
        self.bg_rect.pos = (0, 0) # Windows usually start at (0,0) in FloatLayout

    def start_game(self, dt):
        """Handles initial game rendering. Auto-load disabled per user request."""
        StorageManager.cleanup_old_files(days=7)
        self.render_game()

    def on_window_resize(self, window, width, height):
        self.render_game()

    def render_game(self, *args):
        """Renders the current game state with dynamic scaling."""
        self.clear_widgets()
        self.targets = []
        
        is_won = self.game.check_win()
        # Block UI if won or any dialog is showing
        ui_blocked = is_won or self.auto_finish_asking or self.new_game_asking or self.auto_finish_active

        # Dynamic Scaling based on Window Width
        side_margin = Window.width * 0.03
        available_width = Window.width - 2 * side_margin
        card_w = available_width / 7.5 # Leave some room for gaps
        gap = (available_width - 7 * card_w) / 6
        card_h = card_w * 1.5
        
        # Responsive font sizes
        font_sz = max(12, int(Window.width / 30))
        
        # Font for Chinese support (Cross-platform)
        font_path = os.path.join(os.path.dirname(__file__), "assets", "NotoSansTC-Regular.ttf")
        self.font_name = font_path if os.path.exists(font_path) else None

        # Row Y coordinates
        # Row 1: Controls
        undo_h = max(30, int(Window.height * 0.05))
        undo_y = Window.height - side_margin - undo_h
        
        # Row 2: Stock, Waste, Foundations
        top_row_y = undo_y - side_margin - card_h
        
        # Row 3: Tableaus
        tableau_y = top_row_y - card_h * 0.4 - card_h

        # Undo Button
        undo_btn = Button(text=self.strings.get("undo", "Undo"), size_hint=(None, None), size=(card_w * 1.4, undo_h), 
                          pos=(side_margin, undo_y), font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
        undo_btn.bind(on_release=self.undo_move)
        self.apply_ui_style(undo_btn)
        self.add_widget(undo_btn)

        # New Game Button
        new_game_btn = Button(text=self.strings.get("new_game", "New Game"), size_hint=(None, None), size=(card_w * 1.8, undo_h), 
                             pos=(side_margin + card_w * 1.4 + gap, undo_y), font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
        new_game_btn.bind(on_release=self.reset_game)
        self.apply_ui_style(new_game_btn)
        self.add_widget(new_game_btn)

        # Save Button
        save_btn = Button(text=self.strings.get("save", "Save"), size_hint=(None, None), size=(card_w * 1.2, undo_h), 
                          pos=(side_margin + card_w * 3.2 + 2 * gap, undo_y), font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
        save_btn.bind(on_release=self.save_game)
        self.apply_ui_style(save_btn)
        self.add_widget(save_btn)

        # Load Button
        load_btn = Button(text=self.strings.get("load", "Load"), size_hint=(None, None), size=(card_w * 1.2, undo_h), 
                          pos=(side_margin + card_w * 4.4 + 3 * gap, undo_y), font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
        load_btn.bind(on_release=self.load_game)
        self.apply_ui_style(load_btn)
        self.add_widget(load_btn)

        # Exit Button
        exit_btn = Button(text=self.strings.get("exit", "Exit"), size_hint=(None, None), size=(card_w * 1.2, undo_h), 
                          pos=(side_margin + card_w * 5.6 + 4 * gap, undo_y), font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
        exit_btn.bind(on_release=self.confirm_exit)
        self.apply_ui_style(exit_btn)
        self.add_widget(exit_btn)

        stock_pos = (side_margin, top_row_y)
        if self.game.stock.cards:
            stock_img = "assets/cards/back.png"
            if os.path.exists(stock_img):
                stock_btn = Button(
                    background_normal=stock_img, background_down=stock_img,
                    size_hint=(None, None), size=(card_w, card_h),
                    pos=stock_pos, border=(0, 0, 0, 0), disabled=ui_blocked
                )
            else:
                stock_btn = Button(text="Stock", size_hint=(None, None), size=(card_w, card_h), 
                                   pos=stock_pos, font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
            stock_btn.bind(on_release=self.draw_card)
            self.add_widget(stock_btn)
        else:
            recycle_btn = Button(text=self.strings.get("stock_empty", "Empty"), size_hint=(None, None), size=(card_w, card_h), 
                                 pos=stock_pos, halign='center', font_size=font_sz, disabled=ui_blocked,
                                 background_normal='', background_color=(0.4, 0.4, 0.4, 1), font_name=self.font_name)
            recycle_btn.bind(on_release=self.draw_card)
            self.add_widget(recycle_btn)

        # Waste
        waste_pos = (side_margin + card_w + gap, top_row_y)
        waste_target = PileTarget(text=self.strings.get("waste_label", "W"), size_hint=(None, None), size=(card_w, card_h), 
                                  pos=waste_pos, font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
        waste_target.target_pile = self.game.waste
        self.add_widget(waste_target)
        self.targets.append((waste_target, self.game.waste))
        if self.game.waste.cards:
            # Show up to 2 cards fanned horizontally (top and one below)
            num_to_show = min(len(self.game.waste.cards), 2)
            fan_offset = card_w * 0.35 # 35% horizontal offset
            
            # Draw cards from bottom to top
            start_idx = len(self.game.waste.cards) - num_to_show
            for idx, i in enumerate(range(start_idx, len(self.game.waste.cards))):
                card = self.game.waste.cards[i]
                is_top = (i == len(self.game.waste.cards) - 1)
                # Offset the top card to the right so the one below is visible
                current_x = waste_pos[0] + (idx * fan_offset)
                card_w_widget = CardWidget(card, self.game.waste, card_size=(card_w, card_h), pos=(current_x, waste_pos[1]))
                
                if ui_blocked or not is_top: 
                    card_w_widget.disabled = True
                
                self.add_widget(card_w_widget)
                # Only the top-most widget at its specific fanned position acts as a target
                self.targets.append((card_w_widget, self.game.waste))

        # Foundations (Right-aligned)
        foundation_start_x = Window.width - side_margin - (4 * card_w + 3 * gap)
        for i, foundation in enumerate(self.game.foundations):
            pos = (foundation_start_x + i * (card_w + gap), top_row_y)
            f_target = PileTarget(text=self.strings.get("foundation_label", "F"), size_hint=(None, None), size=(card_w, card_h), 
                                  pos=pos, font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
            f_target.target_pile = foundation
            self.add_widget(f_target)
            self.targets.append((f_target, foundation))
            if foundation.cards:
                card_w_widget = CardWidget(foundation.peek(), foundation, card_size=(card_w, card_h), pos=pos)
                if ui_blocked: card_w_widget.disabled = True
                self.add_widget(card_w_widget)
                self.targets.append((card_w_widget, foundation))

        # Tableaus
        vertical_offset = card_h * 0.20 # Overlap amount
        for i, tableau in enumerate(self.game.tableaus):
            base_pos = (side_margin + i * (card_w + gap), tableau_y)
            t_target = PileTarget(text=self.strings.get("tableau_label", "T"), size_hint=(None, None), size=(card_w, card_h), 
                                  pos=base_pos, font_size=font_sz, disabled=ui_blocked, font_name=self.font_name)
            t_target.target_pile = tableau
            self.add_widget(t_target)
            self.targets.append((t_target, tableau))
            for j, card in enumerate(tableau.cards):
                pos = (side_margin + i * (card_w + gap), tableau_y - (j * vertical_offset))
                card_w_widget = CardWidget(card, tableau, card_size=(card_w, card_h), pos=pos)
                if ui_blocked: card_w_widget.disabled = True
                self.add_widget(card_w_widget)
                self.targets.append((card_w_widget, tableau))


        if is_won:
            self.show_win_screen()
        elif self.auto_finish_asking:
            self.show_auto_finish_dialog()
        elif self.new_game_asking:
            self.show_new_game_dialog()
        elif self.exit_asking:
            self.show_exit_dialog()
        else:
            # Check for auto-finish if not already won
            self.check_auto_finish()


class SolitaireApp(App):
    def build(self):
        return GameLayout()

    def on_stop(self):
        LogManager.stop()


if __name__ == '__main__':
    SolitaireApp().run()
