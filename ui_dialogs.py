from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

class DialogMixin:
    """Mixin for GameLayout to handle dialog overlays."""

    def show_auto_finish_dialog(self):
        """Shows a dialog asking the user if they want to auto-finish."""
        # Create an overlay with a background to capture all touches
        overlay = FloatLayout(size_hint=(1, 1))
        with overlay.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 0.7) # Semi-transparent black
            self.dialog_rect = Rectangle(size=Window.size, pos=(0, 0))
        
        # Keep background rectangle updated on resize
        overlay.bind(size=self._update_dialog_rect, pos=self._update_dialog_rect)

        label = Label(text=self.strings.get("auto_finish_ask", "Auto Finish?"), 
                      font_size='30sp', pos_hint={'center_x': 0.5, 'center_y': 0.6}, font_name=self.font_name)
        
        btn_layout = FloatLayout(size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        
        yes_btn = Button(text=self.strings.get("auto_finish_yes", "Yes"), 
                         size_hint=(0.35, 0.7), pos_hint={'center_x': 0.28, 'center_y': 0.5}, font_name=self.font_name)
        no_btn = Button(text=self.strings.get("auto_finish_no", "No"), 
                        size_hint=(0.35, 0.7), pos_hint={'center_x': 0.72, 'center_y': 0.5}, font_name=self.font_name)
        
        self.apply_ui_style(yes_btn, color_type="green")
        self.apply_ui_style(no_btn, color_type="red")
        
        def on_yes(instance):
            self.auto_finish_asking = False
            self.auto_finish_confirmed = True
            self.auto_finish_active = True
            self.auto_finish_step(0)
            
        def on_no(instance):
            self.auto_finish_asking = False
            self.auto_finish_confirmed = False
            self.render_game() # Clear the dialog
            
        yes_btn.bind(on_release=on_yes)
        no_btn.bind(on_release=on_no)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        
        overlay.add_widget(label)
        overlay.add_widget(btn_layout)
        self.add_widget(overlay)

    def _update_dialog_rect(self, instance, value):
        self.dialog_rect.pos = instance.pos
        self.dialog_rect.size = instance.size

    def show_new_game_dialog(self):
        """Shows a confirmation dialog for starting a new game."""
        overlay = FloatLayout(size_hint=(1, 1))
        with overlay.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 0.7)
            self.new_game_dialog_rect = Rectangle(size=Window.size, pos=(0, 0))
        overlay.bind(size=self._update_dialog_bg, pos=self._update_dialog_bg)

        label = Label(text=self.strings.get("new_game_ask", "Start New Game?"), 
                      font_size='30sp', pos_hint={'center_x': 0.5, 'center_y': 0.6}, font_name=self.font_name)
        
        btn_layout = FloatLayout(size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        yes_btn = Button(text=self.strings.get("new_game_yes", "New Game"), 
                         size_hint=(0.35, 0.7), pos_hint={'center_x': 0.28, 'center_y': 0.5}, font_name=self.font_name)
        no_btn = Button(text=self.strings.get("new_game_no", "Cancel"), 
                        size_hint=(0.35, 0.7), pos_hint={'center_x': 0.72, 'center_y': 0.5}, font_name=self.font_name)
        
        self.apply_ui_style(yes_btn, color_type="green")
        self.apply_ui_style(no_btn, color_type="red")
        
        def on_confirm(instance):
            self.new_game_asking = False
            self.confirm_reset()

        def on_cancel(instance):
            self.new_game_asking = False
            self.render_game()

        yes_btn.bind(on_release=on_confirm)
        no_btn.bind(on_release=on_cancel)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        overlay.add_widget(label)
        overlay.add_widget(btn_layout)
        self.add_widget(overlay)

    def _update_dialog_bg(self, instance, value):
        self.new_game_dialog_rect.size = value
        self.new_game_dialog_rect.pos = instance.pos

    def show_win_screen(self):
        # Create an overlay with a background to capture all touches
        overlay = FloatLayout(size_hint=(1, 1))
        with overlay.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 0.7) # Semi-transparent black
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        
        # Keep background rectangle updated on resize
        overlay.bind(size=self._update_rect, pos=self._update_rect)

        label = Label(text=self.strings.get("win_message", "YOU WIN!"), font_size='40sp', 
                      pos_hint={'center_x': 0.5, 'center_y': 0.6}, font_name=self.font_name)
        
        btn_layout = FloatLayout(size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        new_btn = Button(text=self.strings.get("play_again", "Play Again"), 
                         size_hint=(0.4, 0.7), pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
                         font_name=self.font_name, font_size='20sp')
        
        self.apply_ui_style(new_btn)
        new_btn.bind(on_release=self.confirm_reset)
        
        btn_layout.add_widget(new_btn)
        overlay.add_widget(label)
        overlay.add_widget(btn_layout)
        self.add_widget(overlay)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def show_exit_dialog(self):
        """Shows a confirmation dialog for exiting the game."""
        overlay = FloatLayout(size_hint=(1, 1))
        with overlay.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 0.7)
            self.exit_dialog_rect = Rectangle(size=Window.size, pos=(0, 0))
        overlay.bind(size=self._update_exit_bg, pos=self._update_exit_bg)

        label = Label(text=self.strings.get("exit_ask", "Exit Game?"), 
                      font_size='30sp', pos_hint={'center_x': 0.5, 'center_y': 0.6}, font_name=self.font_name)
        
        btn_layout = FloatLayout(size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        yes_btn = Button(text=self.strings.get("exit_yes", "Exit"), 
                         size_hint=(0.35, 0.7), pos_hint={'center_x': 0.28, 'center_y': 0.5}, font_name=self.font_name)
        no_btn = Button(text=self.strings.get("exit_no", "Cancel"), 
                        size_hint=(0.35, 0.7), pos_hint={'center_x': 0.72, 'center_y': 0.5}, font_name=self.font_name)
        
        self.apply_ui_style(yes_btn, color_type="green")
        self.apply_ui_style(no_btn, color_type="red")
        
        def on_confirm(instance):
            from kivy.app import App
            App.get_running_app().stop()

        def on_cancel(instance):
            self.exit_asking = False
            self.render_game()

        yes_btn.bind(on_release=on_confirm)
        no_btn.bind(on_release=on_cancel)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        overlay.add_widget(label)
        overlay.add_widget(btn_layout)
        self.add_widget(overlay)

    def _update_exit_bg(self, instance, value):
        self.exit_dialog_rect.size = value
        self.exit_dialog_rect.pos = instance.pos
