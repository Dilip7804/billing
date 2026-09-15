# stock_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from database import get_stock_inventory

class StockScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def on_enter(self):
        self.load_stock_data()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=6)
        
        # Top Bar (Back Button & Title)
        top_bar = BoxLayout(size_hint_y=None, height=40, spacing=4)
        btn_back = Button(
            text='< Back', 
            size_hint_x=None, 
            width=70,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=13
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        top_bar.add_widget(btn_back)
        
        title_lbl = Label(
            text='[b]LIVE STOCK INVENTORY[/b]', 
            markup=True, 
            font_size=14, 
            halign='center', 
            color=(0.2, 0.9, 0.5, 1)
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        top_bar.add_widget(title_lbl)
        main_layout.add_widget(top_bar)
        
        # Search Box Section (Input + Search Button)
        search_box = BoxLayout(size_hint_y=None, height=38, spacing=6)
        search_box.add_widget(Label(text='Search:', font_size=11, size_hint_x=None, width=50, bold=True))
        
        self.search_input = TextInput(
            hint_text='Type item name or barcode...', 
            multiline=False, 
            font_size=12,
            size_hint_x=1
        )
        # Jaise hi type karein, turant filter ho jaye
        self.search_input.bind(text=lambda instance, value: self.load_stock_data())
        search_box.add_widget(self.search_input)
        
        btn_search = Button(
            text='🔍 SEARCH', 
            size_hint_x=None, 
            width=85,
            background_color=(0.1, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=11
        )
        btn_search.bind(on_press=lambda x: self.load_stock_data())
        search_box.add_widget(btn_search)
        
        main_layout.add_widget(search_box)
        
        # Summary Info Label
        self.summary_lbl = Label(
            text='Total Filtered Items: 0',
            font_size=12,
            bold=True,
            size_hint_y=None,
            height=28,
            color=(1, 0.9, 0.4, 1)
        )
        main_layout.add_widget(self.summary_lbl)
        
        # Table Header
        header_layout = BoxLayout(size_hint_y=None, height=28, spacing=2)
        header_layout.add_widget(Label(text='[b]Item Name[/b]', markup=True, font_size=11, size_hint_x=1, halign='left'))
        header_layout.add_widget(Label(text='[b]Total Aaya[/b]', markup=True, font_size=11, size_hint_x=None, width=80, halign='center'))
        header_layout.add_widget(Label(text='[b]Total Bika[/b]', markup=True, font_size=11, size_hint_x=None, width=80, halign='center'))
        header_layout.add_widget(Label(text='[b]Balance Bacha[/b]', markup=True, font_size=11, size_hint_x=None, width=90, halign='center'))
        main_layout.add_widget(header_layout)
        
        # Stock List ScrollView
        self.stock_layout = GridLayout(cols=1, spacing=3, size_hint_y=None)
        self.stock_layout.bind(minimum_height=self.stock_layout.setter('height'))
        
        stock_scroll = ScrollView(size_hint_y=1)
        stock_scroll.add_widget(self.stock_layout)
        main_layout.add_widget(stock_scroll)
        
        self.add_widget(main_layout)

    def load_stock_data(self):
        self.stock_layout.clear_widgets()
        query = self.search_input.text.strip().lower()
        
        stock_data = get_stock_inventory()
        
        total_items = 0
        
        for item_name, total_in, total_sold, balance in stock_data:
            # Item name ya query match karne ke liye check
            if query and query not in item_name.lower():
                continue
                
            total_items += 1
            
            row = BoxLayout(size_hint_y=None, height=36, spacing=2, padding=2)
            
            with row.canvas.before:
                Color(0.18, 0.18, 0.18, 1)
                row.rect = Rectangle(pos=row.pos, size=row.size)
            
            def update_bg(instance, value):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(0.18, 0.18, 0.18, 1)
                    Rectangle(pos=instance.pos, size=instance.size)
            row.bind(pos=update_bg, size=update_bg)
            
            balance_color = (0.2, 0.9, 0.5, 1) if balance > 5 else (0.9, 0.3, 0.3, 1)
            
            row.add_widget(Label(text=item_name, font_size=11, size_hint_x=1, halign='left', color=(1, 1, 1, 1)))
            row.add_widget(Label(text=f"{total_in:.1f}", font_size=11, size_hint_x=None, width=80, halign='center', color=(0.4, 0.8, 1, 1)))
            row.add_widget(Label(text=f"{total_sold:.1f}", font_size=11, size_hint_x=None, width=80, halign='center', color=(1, 0.6, 0.4, 1)))
            row.add_widget(Label(text=f"{balance:.1f}", font_size=11, size_hint_x=None, width=90, halign='center', bold=True, color=balance_color))
            
            self.stock_layout.add_widget(row)
            
        self.summary_lbl.text = f"Total Filtered Items: {total_items}"