"""Kivy UI for the Solitaire game with Polished Drag-Drop."""

import os
import sys

# Fix for Android "Permission Denied" when copying logo/config
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

from kivy.config import Config
# CRITICAL: Config.set must be called BEFORE other Kivy imports
Config.set('graphics', 'width', '780')
Config.set('graphics', 'height', '360')
Config.set('graphics', 'multisamples', '0') # Performance boost

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

from logic import GameState
from storage import StorageManager
from logger import LogManager
from ui_widgets import CardWidget, PileTarget
from ui_dialogs import DialogMixin
from ui_mixins import BaseUIMixin, GameActionMixin
from constants import (
    COLOR_BOARD_GREEN, LANDSCAPE_SIDEBAR_W_RATIO, LANDSCAPE_SIDE_MARGIN_RATIO,
    LANDSCAPE_CARD_H_RATIO, LANDSCAPE_ROW_GAP_RATIO, LANDSCAPE_TABLEAU_OFFSET,
    PORTRAIT_SIDE_MARGIN_RATIO, PORTRAIT_CARD_W_RATIO, PORTRAIT_ROW_GAP_RATIO,
    PORTRAIT_TABLEAU_OFFSET, BOTTOM_SAFE_MARGIN, CARD_ASPECT_RATIO
)

class GameLayout(FloatLayout, BaseUIMixin, GameActionMixin, DialogMixin):
    """Main layout for the Solitaire game."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        LogManager.start()
        
        with self.canvas.before:
            Color(*COLOR_BOARD_GREEN)
            self.bg_rect = Rectangle(size=Window.size, pos=(0, 0))
        Window.bind(size=self._update_bg)

        self.game = GameState()
        self.targets = [] 
        self.auto_finish_prompted = False
        self.auto_finish_confirmed = False
        self.auto_finish_asking = False
        self.auto_finish_active = False
        self.new_game_asking = False
        self.exit_asking = False
        self.load_strings()
        
        font_path = os.path.join(os.path.dirname(__file__), "assets", "NotoSansTC-Regular.ttf")
        self.font_name = font_path if os.path.exists(font_path) else None
        
        Window.bind(on_resize=self.on_window_resize)
        Window.bind(on_keyboard=self.on_key)
        Clock.schedule_once(self.start_game)

    def on_key(self, window, keycode, *args):
        if keycode == 27:
            if not (self.auto_finish_asking or self.new_game_asking or self.exit_asking or self.game.check_win()):
                self.confirm_exit(None)
                return True
        return False

    def _update_bg(self, instance, value):
        self.bg_rect.size = value
        self.bg_rect.pos = (0, 0)

    def start_game(self, dt):
        StorageManager.cleanup_old_files(days=7)
        self.render_game()

    def on_window_resize(self, window, width, height):
        self.render_game()

    def _calculate_layout(self):
        """Calculates all positions and sizes based on current orientation."""
        is_landscape = Window.width > Window.height
        
        if is_landscape:
            sidebar_w = Window.width * LANDSCAPE_SIDEBAR_W_RATIO
            game_area_w = Window.width - sidebar_w
            side_margin = game_area_w * LANDSCAPE_SIDE_MARGIN_RATIO
            
            card_h = Window.height / LANDSCAPE_CARD_H_RATIO
            card_w = card_h / CARD_ASPECT_RATIO
            gap = (game_area_w - 2 * side_margin - 7 * card_w) / 6
            
            font_sz = max(10, int(Window.height / 28))
            
            btn_w, btn_h = sidebar_w * 0.85, Window.height / 8
            btn_x = (sidebar_w - btn_w) / 2
            btn_spacing = (Window.height - 5 * btn_h) / 6
            btn_pos = [(btn_x, Window.height - (i+1)*btn_spacing - (i+1)*btn_h) for i in range(5)]
            btn_sizes = [(btn_w, btn_h)] * 5
            
            top_row_y = Window.height - Window.height * 0.01 - card_h
            tableau_y = top_row_y - card_h * LANDSCAPE_ROW_GAP_RATIO - card_h
            game_start_x = sidebar_w + side_margin
            tab_offset = card_h * LANDSCAPE_TABLEAU_OFFSET
        else:
            sidebar_w = 0
            side_margin = Window.width * PORTRAIT_SIDE_MARGIN_RATIO
            card_w = Window.width / PORTRAIT_CARD_W_RATIO
            card_h = card_w * CARD_ASPECT_RATIO
            gap = (Window.width - 2 * side_margin - 7 * card_w) / 6
            
            font_sz = max(12, int(Window.width / 30))
            undo_h = max(30, int(Window.height * 0.05))
            undo_y = Window.height - side_margin - undo_h
            
            btn_pos = [
                (side_margin, undo_y),
                (side_margin + card_w * 1.4 + gap, undo_y),
                (side_margin + card_w * 3.2 + 2 * gap, undo_y),
                (side_margin + card_w * 4.4 + 3 * gap, undo_y),
                (side_margin + card_w * 5.6 + 4 * gap, undo_y),
            ]
            btn_sizes = [(card_w * 1.4, undo_h), (card_w * 1.8, undo_h), (card_w * 1.2, undo_h), (card_w * 1.2, undo_h), (card_w * 1.2, undo_h)]
            
            top_row_y = undo_y - side_margin - card_h
            tableau_y = top_row_y - card_h * PORTRAIT_ROW_GAP_RATIO - card_h
            game_start_x = side_margin
            tab_offset = card_h * PORTRAIT_TABLEAU_OFFSET

        return {
            'card_w': card_w, 'card_h': card_h, 'gap': gap, 'font_sz': font_sz,
            'btn_pos': btn_pos, 'btn_sizes': btn_sizes, 'top_row_y': top_row_y,
            'tableau_y': tableau_y, 'game_start_x': game_start_x, 'tab_offset': tab_offset,
            'sidebar_w': sidebar_w, 'side_margin': side_margin
        }

    def render_game(self, *args):
        self.clear_widgets()
        self.targets = []
        is_won = self.game.check_win()
        ui_blocked = is_won or self.auto_finish_asking or self.new_game_asking or self.auto_finish_active
        
        layout = self._calculate_layout()
        self._render_controls(layout, ui_blocked)
        self._render_stock_waste(layout, ui_blocked)
        self._render_foundations(layout, ui_blocked)
        self._render_tableaus(layout, ui_blocked)

        if is_won: self.show_win_screen()
        elif self.auto_finish_asking: self.show_auto_finish_dialog()
        elif self.new_game_asking: self.show_new_game_dialog()
        elif self.exit_asking: self.show_exit_dialog()
        else: self.check_auto_finish()

    def _render_controls(self, layout, ui_blocked):
        btns_data = [("undo", self.undo_move), ("new_game", self.reset_game), ("save", self.save_game), ("load", self.load_game), ("exit", self.confirm_exit)]
        for i, (key, callback) in enumerate(btns_data):
            btn = Button(text=self.strings.get(key, key.capitalize()), size_hint=(None, None), 
                         size=layout['btn_sizes'][i], pos=layout['btn_pos'][i], font_size=layout['font_sz'], 
                         disabled=ui_blocked, font_name=self.font_name)
            btn.bind(on_release=callback)
            self.apply_ui_style(btn)
            self.add_widget(btn)

    def _render_stock_waste(self, layout, ui_blocked):
        stock_pos = (layout['game_start_x'], layout['top_row_y'])
        if self.game.stock.cards:
            img = "assets/cards/back.png"
            stock_btn = Button(background_normal=img, background_down=img, size_hint=(None, None), 
                               size=(layout['card_w'], layout['card_h']), pos=stock_pos, border=(0, 0, 0, 0), disabled=ui_blocked)
            stock_btn.bind(on_release=self.draw_card)
            self.add_widget(stock_btn)
        else:
            recycle_btn = Button(text=self.strings.get("stock_empty", "Empty"), size_hint=(None, None), 
                                 size=(layout['card_w'], layout['card_h']), pos=stock_pos, halign='center', 
                                 font_size=layout['font_sz'], disabled=ui_blocked, background_normal='', 
                                 background_color=(0.4, 0.4, 0.4, 1), font_name=self.font_name)
            recycle_btn.bind(on_release=self.draw_card)
            self.add_widget(recycle_btn)

        waste_pos = (layout['game_start_x'] + layout['card_w'] + layout['gap'], layout['top_row_y'])
        waste_target = PileTarget(text=self.strings.get("waste_label", "W"), size_hint=(None, None), 
                                  size=(layout['card_w'], layout['card_h']), pos=waste_pos, 
                                  font_size=layout['font_sz'], disabled=ui_blocked, font_name=self.font_name)
        waste_target.target_pile = self.game.waste
        self.add_widget(waste_target)
        self.targets.append((waste_target, self.game.waste))
        
        if self.game.waste.cards:
            num_to_show = min(len(self.game.waste.cards), 2)
            fan_offset = layout['card_w'] * 0.35
            start_idx = len(self.game.waste.cards) - num_to_show
            for idx, i in enumerate(range(start_idx, len(self.game.waste.cards))):
                card = self.game.waste.cards[i]
                is_top = (i == len(self.game.waste.cards) - 1)
                pos = (waste_pos[0] + idx * fan_offset, waste_pos[1])
                cw = CardWidget(card, self.game.waste, card_size=(layout['card_w'], layout['card_h']), pos=pos)
                if ui_blocked or not is_top: cw.disabled = True
                self.add_widget(cw)
                self.targets.append((cw, self.game.waste))

    def _render_foundations(self, layout, ui_blocked):
        is_landscape = Window.width > Window.height
        side_margin = (Window.width - layout['sidebar_w']) * LANDSCAPE_SIDE_MARGIN_RATIO if is_landscape else Window.width * PORTRAIT_SIDE_MARGIN_RATIO
        foundation_start_x = Window.width - side_margin - (4 * layout['card_w'] + 3 * layout['gap'])
        
        for i, foundation in enumerate(self.game.foundations):
            pos = (foundation_start_x + i * (layout['card_w'] + layout['gap']), layout['top_row_y'])
            f_target = PileTarget(text=self.strings.get("foundation_label", "F"), size_hint=(None, None), 
                                  size=(layout['card_w'], layout['card_h']), pos=pos, 
                                  font_size=layout['font_sz'], disabled=ui_blocked, font_name=self.font_name)
            f_target.target_pile = foundation
            self.add_widget(f_target)
            self.targets.append((f_target, foundation))
            if foundation.cards:
                cw = CardWidget(foundation.peek(), foundation, card_size=(layout['card_w'], layout['card_h']), pos=pos)
                if ui_blocked: cw.disabled = True
                self.add_widget(cw)
                self.targets.append((cw, foundation))

    def _render_tableaus(self, layout, ui_blocked):
        bottom_limit = Window.height * BOTTOM_SAFE_MARGIN
        for i, tableau in enumerate(self.game.tableaus):
            base_pos = (layout['game_start_x'] + i * (layout['card_w'] + layout['gap']), layout['tableau_y'])
            t_target = PileTarget(text=self.strings.get("tableau_label", "T"), size_hint=(None, None), 
                                  size=(layout['card_w'], layout['card_h']), pos=base_pos, 
                                  font_size=layout['font_sz'], disabled=ui_blocked, font_name=self.font_name)
            t_target.target_pile = tableau
            self.add_widget(t_target)
            self.targets.append((t_target, tableau))
            
            num_cards = len(tableau.cards)
            if num_cards > 0:
                available_space = layout['tableau_y'] - bottom_limit
                current_offset = min(layout['tab_offset'], available_space / (num_cards - 1)) if num_cards > 1 else layout['tab_offset']
                for j, card in enumerate(tableau.cards):
                    pos = (base_pos[0], layout['tableau_y'] - (j * current_offset))
                    cw = CardWidget(card, tableau, card_size=(layout['card_w'], layout['card_h']), pos=pos)
                    if ui_blocked: cw.disabled = True
                    self.add_widget(cw)
                    self.targets.append((cw, tableau))

class SolitaireApp(App):
    def build(self):
        return GameLayout()

    def on_stop(self):
        LogManager.stop()

if __name__ == '__main__':
    SolitaireApp().run()
