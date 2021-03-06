import sys

import os
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivymd.theming import ThemeManager

from libs.config import MarkdownNotebookConfig
from main import __version__ as app_version
from uix.start_screen import StartScreen
from uix.widget import ThemePicker


class BaseApp(App):
    icon = 'icon.png'
    nav_drawer = ObjectProperty()
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Blue'

    def __init__(self, base_screen_name, base_screen_title, **kvargs):
        super().__init__(**kvargs)
        Window.bind(on_keyboard=self.events_program)
        Window.soft_input_mode = 'below_target'

        self.base_screen_name = base_screen_name
        self.base_screen_title = base_screen_title
        self.previous_screens = [base_screen_name]
        self.window = Window
        self.manager = None
        self.exit_interval = False

    def build_config(self, config):
        self.config = MarkdownNotebookConfig(self.config)

    def build(self):
        self.screen = StartScreen()
        self.manager = self.screen.ids.manager
        self.nav_drawer = self.screen.ids.nav_drawer
        self.screen.ids.about_screen.build(app_version, self.theme_cls.primary_color)

        self.config.load_theme(self.theme_cls)
        self.theme_picker = ThemePicker(self.config, self.theme_cls)

        return self.screen

    def show_about(self, *args):
        self.screen.ids.action_bar.title = 'About'
        self.nav_drawer.toggle_nav_drawer()
        self.manager.current = 'about_screen'
        self.screen.ids.action_bar.left_action_items = \
            [['chevron-left', lambda x: self.back_screen()]]

    def get_application_config(self, defaultpath=None):
        return super().get_application_config(os.path.join(self.directory, f'{self.name}.ini'))

    def events_program(self, instance, keyboard, keycode, text, modifiers):
        """
        27 - Esc
        1001 - ?
        282 - ?
        319 - ?
        """

        if keyboard in (1001, 27):
            if self.nav_drawer.state == 'open':
                self.nav_drawer.toggle_nav_drawer()

            self.back_screen()
        elif keyboard in (282, 319):
            pass

        return True

    def back_screen(self):
        if self.manager.current == self.base_screen_name:
            self.dialog_exit()
            return

        try:
            self.manager.current = self.previous_screens.pop()
        except:
            self.manager.current = self.base_screen_name

        self.screen.ids.action_bar.title = self.base_screen_title
        self.screen.ids.action_bar.left_action_items = [['menu', lambda x: self.nav_drawer._toggle()]]

    def dialog_exit(self):
        def check_interval_press(interval):
            self.exit_interval += interval
            if self.exit_interval > 5:
                self.exit_interval = False
                Clock.unschedule(check_interval_press)

        if self.exit_interval:
            sys.exit(0)

        Clock.schedule_interval(check_interval_press, 0.1)

    def theme_picker_open(self, *args):
        self.theme_picker.open()
