# dashboard_screen.py

import sqlite3
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def on_enter(self):
        self.update_sales_stats()

    def build_ui(self):
        # Main layout anchored strictly to the top with optimal compact padding
        outer_layout = BoxLayout(
            orientation='vertical', 
            padding=[10, 8, 10, 8], 
            spacing=6,
            size_hint=(1, 1),
            pos_hint={'top': 1, 'center_x': 0.5}
        )
        
        # 1. TOP HEADER BANNER
        header_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=38, padding=[5, 2])
        with header_layout.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_rect = RoundedRectangle(pos=header_layout.pos, size=header_layout.size, radius=[6])
        header_layout.bind(pos=lambda *x: setattr(self.header_rect, 'pos', header_layout.pos),
                           size=lambda *x: setattr(self.header_rect, 'size', header_layout.size))
        
        title = Label(
            text='[b]MERA STORE[/b]  •  Dashboard', 
            markup=True, 
            font_size=15, 
            halign='center',
            valign='middle',
            color=(0.95, 0.95, 0.95, 1)
        )
        title.bind(size=title.setter('text_size'))
        header_layout.add_widget(title)
        outer_layout.add_widget(header_layout)

        # 2. STATS CARDS (Today's Sale & Total Revenue)
        stats_main_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=52, spacing=6)
        
        # Box A: Today's Sale
        self.today_box = BoxLayout(orientation='vertical', padding=3)
        with self.today_box.canvas.before:
            Color(0.15, 0.22, 0.30, 1)
            self.today_rect = RoundedRectangle(pos=self.today_box.pos, size=self.today_box.size, radius=[6])
        self.today_box.bind(pos=lambda *x: setattr(self.today_rect, 'pos', self.today_box.pos),
                            size=lambda *x: setattr(self.today_rect, 'size', self.today_box.size))
        
        self.today_label = Label(
            text='[b]TODAY SALE[/b]\n₹0.00',
            markup=True,
            font_size=11,
            halign='center',
            valign='middle',
            color=(0.3, 0.9, 0.5, 1)
        )
        self.today_label.bind(size=self.today_label.setter('text_size'))
        self.today_box.add_widget(self.today_label)
        stats_main_box.add_widget(self.today_box)

        # Box B: Total Revenue
        self.total_box = BoxLayout(orientation='vertical', padding=3)
        with self.total_box.canvas.before:
            Color(0.22, 0.18, 0.28, 1)
            self.total_rect = RoundedRectangle(pos=self.total_box.pos, size=self.total_box.size, radius=[6])
        self.total_box.bind(pos=lambda *x: setattr(self.total_rect, 'pos', self.total_box.pos),
                            size=lambda *x: setattr(self.total_rect, 'size', self.total_box.size))
        
        self.total_label = Label(
            text='[b]TOTAL REVENUE[/b]\n₹0.00 (0 Bills)',
            markup=True,
            font_size=11,
            halign='center',
            valign='middle',
            color=(1, 0.85, 0.2, 1)
        )
        self.total_label.bind(size=self.total_label.setter('text_size'))
        self.total_box.add_widget(self.total_label)
        stats_main_box.add_widget(self.total_box)

        outer_layout.add_widget(stats_main_box)
        
        # 3. ACTION BUTTONS (Standard height for proper clickability)
        buttons_data = [
            ('🛒  NEW BILLING', (0.10, 0.60, 0.28, 1), 'billing'),
            ('📊  VIEW SALES REPORTS', (0.85, 0.40, 0.08, 1), 'report'),
            ('📦  CHECK INVENTORY / STOCK', (0.12, 0.48, 0.75, 1), 'stock'),
            ('⚙️  MANAGE OPENING STOCK', (0.48, 0.25, 0.68, 1), 'opening_stock'),
        ]

        for text, bg_color, screen_name in buttons_data:
            btn = Button(
                text=text, 
                size_hint_y=None, 
                height=42,
                background_normal='',
                background_color=bg_color,
                color=(1, 1, 1, 1),
                bold=True,
                font_size=13
            )
            btn.bind(on_press=lambda x, s=screen_name: setattr(self.manager, 'current', s))
            outer_layout.add_widget(btn)

        # 4. FULL-SIZE BOTTOM CALCULATOR (Takes remaining vertical space cleanly)
        calc_main = BoxLayout(orientation='vertical', size_hint_y=1, padding=5, spacing=4)
        with calc_main.canvas.before:
            Color(0.15, 0.17, 0.21, 1)
            self.calc_rect = RoundedRectangle(pos=calc_main.pos, size=calc_main.size, radius=[6])
        calc_main.bind(pos=lambda *x: setattr(self.calc_rect, 'pos', calc_main.pos),
                       size=lambda *x: setattr(self.calc_rect, 'size', calc_main.size))
        
        # Calculator Display Box
        self.calc_input_label = Label(
            text='0',
            font_size=18,
            bold=True,
            halign='right',
            valign='middle',
            size_hint_y=None,
            height=32,
            color=(1, 1, 1, 1)
        )
        self.calc_input_label.bind(size=self.calc_input_label.setter('text_size'))
        calc_main.add_widget(self.calc_input_label)

        # Calculator Keypad (Expands nicely in available space)
        calc_grid = GridLayout(cols=4, spacing=4, size_hint=(1, 1))
        calc_buttons = [
            'C', '(', ')', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '.', '⌫', '='
        ]
        
        for caption in calc_buttons:
            cb = Button(
                text=caption,
                background_normal='',
                background_color=(0.24, 0.27, 0.34, 1) if caption not in ['=', 'C'] else (0.12, 0.55, 0.28, 1) if caption == '=' else (0.7, 0.2, 0.2, 1),
                color=(1, 1, 1, 1),
                bold=True,
                font_size=14
            )
            cb.bind(on_press=self.on_calc_button_press)
            calc_grid.add_widget(cb)
            
        calc_main.add_widget(calc_grid)
        outer_layout.add_widget(calc_main)

        # 5. LOGOUT BUTTON AT THE VERY BOTTOM
        btn_logout = Button(
            text='⮡  LOGOUT SYSTEM', 
            size_hint_y=None, 
            height=36, 
            background_normal='',
            background_color=(0.80, 0.18, 0.18, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=12
        )
        btn_logout.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        outer_layout.add_widget(btn_logout)
        
        self.add_widget(outer_layout)

    def on_calc_button_press(self, instance):
        txt = instance.text
        current_text = self.calc_input_label.text
        
        if current_text in ['0', 'Error', 'Infinity']:
            current_text = ''
            
        if txt == 'C':
            self.calc_input_label.text = '0'
        elif txt == '⌫':
            if len(current_text) > 1:
                self.calc_input_label.text = current_text[:-1]
            else:
                self.calc_input_label.text = '0'
        elif txt == '=':
            try:
                res = str(eval(current_text))
                if res.endswith('.0'):
                    res = res[:-2]
                self.calc_input_label.text = res
            except Exception:
                self.calc_input_label.text = 'Error'
        else:
            if current_text == '' and txt in ['*', '/', '+', ')']:
                return
            self.calc_input_label.text = current_text + txt

    def update_sales_stats(self):
        try:
            conn = sqlite3.connect('store_billing.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*), SUM(grand_total) FROM bills")
            res = cursor.fetchone()
            total_bills = res[0] if res[0] else 0
            total_sales = res[1] if res[1] else 0.0

            today_date = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT SUM(grand_total) FROM bills WHERE date_time LIKE ?", (f"{today_date}%",))
            today_res = cursor.fetchone()
            today_sales = today_res[0] if (today_res and today_res[0]) else 0.0
            
            conn.close()
            
            self.today_label.text = f'[b]TODAY SALE[/b]\n₹{today_sales:.2f}'
            self.total_label.text = f'[b]TOTAL REVENUE[/b]\n₹{total_sales:.2f} ({total_bills} Bills)'
        except Exception:
            self.today_label.text = '[b]TODAY SALE[/b]\n₹0.00'
            self.total_label.text = '[b]TOTAL REVENUE[/b]\n₹0.00 (0 Bills)'