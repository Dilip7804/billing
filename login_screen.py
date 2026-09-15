# login_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from database import check_login

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main container
        layout = BoxLayout(
            orientation='vertical', 
            padding=40, 
            spacing=20, 
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.85, None),
            height=450
        )
        
        # Title
        self.title_lbl = Label(
            text='[b]MERA STORE[/b]', 
            markup=True, 
            font_size=28, 
            size_hint_y=None, 
            height=50,
            halign='center'
        )
        self.title_lbl.bind(size=self.title_lbl.setter('text_size'))
        
        self.subtitle_lbl = Label(
            text='Please login to your account', 
            font_size=16, 
            color=(0.7, 0.7, 0.7, 1), 
            size_hint_y=None, 
            height=30,
            halign='center'
        )
        self.subtitle_lbl.bind(size=self.subtitle_lbl.setter('text_size'))
        
        # Text Inputs
        self.username = TextInput(
            hint_text='Username',
            multiline=False,
            size_hint_y=None,
            height=50
        )
        
        self.password = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=50
        )
        
        # Login Button
        self.login_btn = Button(
            text='LOGIN',
            size_hint_y=None,
            height=50,
            background_color=(0.1, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            bold=True
        )
        self.login_btn.bind(on_press=self.do_login)
        
        # Message Label
        self.msg_label = Label(
            text='', 
            color=(1, 0, 0, 1), 
            size_hint_y=None, 
            height=30,
            halign='center'
        )
        self.msg_label.bind(size=self.msg_label.setter('text_size'))
        
        layout.add_widget(self.title_lbl)
        layout.add_widget(self.subtitle_lbl)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.login_btn)
        layout.add_widget(self.msg_label)
        
        self.add_widget(layout)

    def do_login(self, instance):
        user_text = self.username.text.strip()
        pass_text = self.password.text.strip()
        
        if check_login(user_text, pass_text):
            self.manager.current = 'dashboard'
            self.msg_label.text = ''
            self.username.text = ''
            self.password.text = ''
        else:
            self.msg_label.text = 'Galat Username ya Password!'