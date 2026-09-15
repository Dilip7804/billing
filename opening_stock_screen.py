# opening_stock_screen.py

import sqlite3
import csv
import tkinter as tk
from tkinter import filedialog
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from database import import_vrs_csv, update_item_stock

class OpeningStockScreen(Screen):
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
            text='[b]OPENING STOCK MANAGEMENT[/b]', 
            markup=True, 
            font_size=13, 
            halign='center', 
            color=(0.2, 0.9, 0.5, 1)
        )
        title_lbl.bind(size=title_lbl.setter('text_size'))
        top_bar.add_widget(title_lbl)
        main_layout.add_widget(top_bar)
        
        # Action Buttons Row (Import CSV & Export Excel)
        action_row = BoxLayout(size_hint_y=None, height=38, spacing=6)
        
        btn_import = Button(
            text='🔄 IMPORT CSV', 
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=11
        )
        btn_import.bind(on_press=self.browse_and_import_csv)
        action_row.add_widget(btn_import)
        
        btn_export = Button(
            text='📁 EXPORT EXCEL', 
            background_color=(0.5, 0.1, 0.6, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=11
        )
        btn_export.bind(on_press=self.export_stock_to_csv)
        action_row.add_widget(btn_export)
        
        main_layout.add_widget(action_row)

        # Search Box Section
        search_box = BoxLayout(size_hint_y=None, height=36, spacing=6)
        search_box.add_widget(Label(text='Search:', font_size=11, size_hint_x=None, width=50, bold=True))
        
        self.search_input = TextInput(
            hint_text='Type item name or barcode...', 
            multiline=False, 
            font_size=12,
            size_hint_x=1
        )
        self.search_input.bind(text=lambda instance, value: self.load_stock_data())
        search_box.add_widget(self.search_input)
        main_layout.add_widget(search_box)
        
        # Status Message / Summary
        self.status_lbl = Label(
            text='Total Items: 0',
            font_size=11,
            bold=True,
            size_hint_y=None,
            height=24,
            color=(1, 0.9, 0.4, 1)
        )
        main_layout.add_widget(self.status_lbl)
        
        # Table Header
        header_layout = BoxLayout(size_hint_y=None, height=26, spacing=2)
        header_layout.add_widget(Label(text='[b]Item Name[/b]', markup=True, font_size=11, size_hint_x=1, halign='left'))
        header_layout.add_widget(Label(text='[b]Rate (₹)[/b]', markup=True, font_size=11, size_hint_x=None, width=65, halign='center'))
        header_layout.add_widget(Label(text='[b]Stock Qty[/b]', markup=True, font_size=11, size_hint_x=None, width=75, halign='center'))
        header_layout.add_widget(Label(text='[b]Action[/b]', markup=True, font_size=11, size_hint_x=None, width=65, halign='center'))
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
        
        try:
            conn = sqlite3.connect('store_billing.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, barcode, rate, stock FROM items")
            items = cursor.fetchall()
            conn.close()
        except Exception as e:
            items = []

        total_items = 0
        
        for name, barcode, rate, stock in items:
            if query and query not in name.lower() and query not in barcode.lower():
                continue
                
            total_items += 1
            
            row = BoxLayout(size_hint_y=None, height=38, spacing=2, padding=2)
            
            with row.canvas.before:
                Color(0.18, 0.18, 0.18, 1)
                row.rect = Rectangle(pos=row.pos, size=row.size)
            
            def update_bg(instance, value):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(0.18, 0.18, 0.18, 1)
                    Rectangle(pos=instance.pos, size=instance.size)
            row.bind(pos=update_bg, size=update_bg)
            
            # Item Name Label
            row.add_widget(Label(text=name, font_size=11, size_hint_x=1, halign='left', color=(1, 1, 1, 1)))
            
            # Rate Label
            row.add_widget(Label(text=f"{rate:.2f}", font_size=11, size_hint_x=None, width=65, halign='center', color=(0.4, 0.8, 1, 1)))
            
            # Editable Qty Input
            qty_input = TextInput(
                text=str(stock if stock is not None else 0.0),
                multiline=False,
                font_size=11,
                size_hint_x=None,
                width=75,
                halign='center'
            )
            row.add_widget(qty_input)
            
            # Update Button
            btn_update = Button(
                text='Save',
                size_hint_x=None,
                width=65,
                background_color=(0.1, 0.6, 0.2, 1),
                color=(1, 1, 1, 1),
                bold=True,
                font_size=10
            )
            
            def save_qty(btn, b_code, q_inp):
                try:
                    new_val = float(q_inp.text.strip())
                    success, msg = update_item_stock(b_code, new_val)
                    self.status_lbl.text = msg
                except ValueError:
                    self.status_lbl.text = "Invalid quantity format!"

            btn_update.bind(on_press=lambda x, bc=barcode, qi=qty_input: save_qty(x, bc, qi))
            row.add_widget(btn_update)
            
            self.stock_layout.add_widget(row)
            
        self.status_lbl.text = f"Total Filtered Items: {total_items}"

    def browse_and_import_csv(self, instance):
        try:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select VRS CSV/Excel File",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            root.destroy()
            
            if file_path:
                success, msg = import_vrs_csv(file_path)
                self.status_lbl.text = msg
                self.load_stock_data()
            else:
                self.status_lbl.text = "Koi file select nahi ki gayi."
        except Exception as e:
            self.status_lbl.text = f"Error: {str(e)}"

    def export_stock_to_csv(self, instance):
        try:
            conn = sqlite3.connect('store_billing.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, barcode, rate, stock FROM items")
            records = cursor.fetchall()
            conn.close()
            
            if not records:
                self.status_lbl.text = "Export ke liye koi stock data nahi mila!"
                return
                
            filename = "opening_stock_report.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Item Name", "Barcode", "Rate", "Stock Qty"])
                for row in records:
                    writer.writerow(row)
                    
            self.status_lbl.text = f"Success! Saved as '{filename}'"
        except Exception as e:
            self.status_lbl.text = f"Export Error: {str(e)}"