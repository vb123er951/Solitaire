import os
import json
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line
from storage import StorageManager

class BaseUIMixin:
    """Base UI mixin for general helpers like styling, toasts, and localization."""
    
    def load_strings(self):
        """Loads display strings from JSON, preferring Chinese if available."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        zh_path = os.path.join(base_dir, "assets", "strings_zh.json")
        en_path = os.path.join(base_dir, "assets", "strings.json")
        
        defaults = {
            "undo": "Undo",
            "new_game": "New Game",
            "stock_empty": "Empty",
            "waste_label": "W",
            "foundation_label": "F",
            "tableau_label": "T",
            "win_message": "YOU WIN!",
            "play_again": "Play Again"
        }

        path = zh_path if os.path.exists(zh_path) else en_path
        print(f"DEBUG: Attempting to load strings from: {path}")

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.strings = json.load(f)
                print(f"DEBUG: Successfully loaded strings from {path}")
            except Exception as e:
                print(f"DEBUG: Error loading JSON: {e}")
                self.strings = defaults
        else:
            print(f"DEBUG: Language file not found at {path}, using defaults")
            self.strings = defaults

    def show_toast(self, text):
        """Displays a temporary toast message at the bottom of the screen."""
        toast_h = Window.height * 0.08
        radius = toast_h * 0.2
        
        toast = Label(
            text=text,
            size_hint=(None, None),
            size=(Window.width * 0.8, toast_h),
            pos=(Window.width * 0.1, Window.height * 0.12),
            font_size=max(16, int(Window.width / 22)),
            font_name=self.font_name,
            color=(1, 1, 1, 1)
        )
        
        with toast.canvas.before:
            # Background
            Color(0.1, 0.1, 0.1, 0.85)
            toast.bg_rect = RoundedRectangle(size=toast.size, pos=toast.pos, radius=[radius])
            # Border
            Color(0.4, 0.4, 0.4, 0.5)
            toast.border_line = Line(rounded_rectangle=(toast.x, toast.y, toast.width, toast.height, radius), width=1.1)
        
        def update_toast_graphics(instance, value):
            if hasattr(instance, 'bg_rect'):
                instance.bg_rect.pos = instance.pos
                instance.bg_rect.size = instance.size
                instance.border_line.rounded_rectangle = (instance.x, instance.y, instance.width, instance.height, radius)
        
        toast.bind(pos=update_toast_graphics, size=update_toast_graphics)
        self.add_widget(toast)
        
        anim = Animation(opacity=1, duration=0.3) + \
               Animation(opacity=1, duration=1.5) + \
               Animation(opacity=0, duration=0.7)
        anim.bind(on_complete=lambda *args: self.remove_widget(toast))
        
        toast.opacity = 0
        anim.start(toast)

    def apply_ui_style(self, button, color_type="default"):
        """Applies custom color styles with a 'clicked' feedback effect."""
        button.background_normal = '' 
        button.background_color = (0, 0, 0, 0)
        button.color = (0, 0, 0, 1)
        
        color_map = {
            "green": ((0.6, 0.9, 0.6), (0.4, 0.7, 0.4)),
            "red": ((0.9, 0.6, 0.6), (0.7, 0.4, 0.4)),
            "secondary": ((0.8, 0.8, 0.8), (0.6, 0.6, 0.6)),
            "default": ((0.5, 0.7, 0.9), (0.3, 0.5, 0.7))
        }
        
        colors = color_map.get(color_type, color_map["default"])
        border_color = (0.2, 0.4, 0.6, 0.8)
        if color_type == "green": border_color = (0.3, 0.6, 0.3, 0.8)
        if color_type == "red": border_color = (0.6, 0.3, 0.3, 0.8)

        with button.canvas.before:
            button.bg_color_instr = Color(*colors[0], 1)
            button.bg_rect = RoundedRectangle(size=button.size, pos=button.pos, radius=[5])
            
        with button.canvas.after:
            button.border_color_instr = Color(*border_color)
            button.border_line = Line(rounded_rectangle=(button.x, button.y, button.width, button.height, 5), width=1.1)
        
        def update_graphics(instance, value):
            if hasattr(instance, 'bg_rect'):
                instance.bg_rect.pos = instance.pos
                instance.bg_rect.size = instance.size
                instance.border_line.rounded_rectangle = (instance.x, instance.y, instance.width, instance.height, 5)
                instance.bg_color_instr.rgb = colors[0] if instance.state == 'normal' else colors[1]
        
        button.bind(pos=update_graphics, size=update_graphics, state=update_graphics)

class GameActionMixin:
    """Mixin for GameLayout to handle game-related actions and events."""
    
    def check_auto_finish(self):
        """Triggers automatic card movement if criteria are met."""
        if self.game.can_auto_finish():
            if not self.auto_finish_prompted:
                self.auto_finish_asking = True
                self.auto_finish_prompted = True
                self.render_game()
            elif self.auto_finish_confirmed and not getattr(self, "auto_finish_active", False):
                self.auto_finish_active = True
                Clock.schedule_once(self.auto_finish_step, 0.1)

    def auto_finish_step(self, dt):
        """Moves one card from tableau to foundations automatically."""
        if self.game.check_win():
            self.auto_finish_active = False
            return

        moved = False
        for tableau in self.game.tableaus:
            if not tableau.cards:
                continue
            for foundation in self.game.foundations:
                if self.game.move_card(tableau, foundation):
                    self.render_game()
                    moved = True
                    break
            if moved:
                break
        
        if moved:
            Clock.schedule_once(self.auto_finish_step, 0.1)
        else:
            self.auto_finish_active = False

    def save_game(self, instance):
        if self.game.check_win(): return
        if StorageManager.save_game(self.game):
            self.show_toast(self.strings.get("game_saved", "Game Saved"))
        else:
            print("Failed to save game.")

    def load_game(self, instance):
        if StorageManager.load_game(self.game):
            print("Game loaded successfully.")
            self.auto_finish_prompted = False
            self.auto_finish_confirmed = False
            self.auto_finish_asking = False
            self.auto_finish_active = False
            self.new_game_asking = False
            self.render_game()
            self.show_toast(self.strings.get("game_loaded", "Game Loaded"))
        else:
            self.show_toast(self.strings.get("load_failed", "No Save Found"))
            print("Failed to load game.")

    def draw_card(self, instance):
        if self.game.check_win(): return
        self.game.draw_from_stock()
        self.render_game()

    def undo_move(self, instance):
        if self.game.check_win(): return
        if self.game.undo():
            self.render_game()

    def auto_move(self, card_widget):
        if self.game.check_win(): return
        for foundation in self.game.foundations:
            if self.game.move_card(card_widget.source_pile, foundation):
                self.render_game()
                return
        if card_widget.source_pile.peek() == card_widget.card:
            for tableau in self.game.tableaus:
                if tableau != card_widget.source_pile:
                    if self.game.move_card(card_widget.source_pile, tableau):
                        self.render_game()
                        return

    def handle_drop(self, card_widget):
        """Handles dropping with improved multi-source support and collision."""
        if self.game.check_win(): return
        cx, cy = card_widget.center
        from logic import Foundation, Tableau

        if len(card_widget.stack_widgets) == 1:
            for widget, pile in self.targets:
                if isinstance(pile, Foundation):
                    if widget.collide_point(cx, cy):
                        if self.game.move_card(card_widget.source_pile, pile):
                            self.render_game()
                            return

        for widget, pile in self.targets:
            if isinstance(pile, Tableau) and pile != card_widget.source_pile:
                if widget.collide_point(cx, cy):
                    if isinstance(card_widget.source_pile, Tableau):
                        if self.game.move_stack(card_widget.source_pile, pile, card_widget.card):
                            self.render_game()
                            return
                    else:
                        if len(card_widget.stack_widgets) == 1:
                            if self.game.move_card(card_widget.source_pile, pile):
                                self.render_game()
                                return
        self.render_game()

    def reset_game(self, instance):
        if self.game.check_win():
            self.confirm_reset()
        else:
            self.new_game_asking = True
            self.render_game()

    def confirm_reset(self, *args):
        self.game.reset()
        self.auto_finish_prompted = False
        self.auto_finish_confirmed = False
        self.auto_finish_asking = False
        self.auto_finish_active = False
        self.new_game_asking = False
        self.exit_asking = False
        self.render_game()

    def confirm_exit(self, instance):
        self.exit_asking = True
        self.render_game()
