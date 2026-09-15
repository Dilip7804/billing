# billing_screen.py

import sqlite3
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from database import search_item, search_items_suggestions, save_bill_to_db
from printer import generate_bill_receipt_text

class BillingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []
        self.selected_item_name = None
        self.selected_payment_mode = "CASH"
        self.split_amounts = {"CASH": 0.0, "UPI": 0.0, "CARD": 0.0}
        self.build_ui()

    def on_enter(self):
        self.date_lbl.text = datetime.now().strftime("%d-%m-%Y")
        self.generate_invoice_number()

    def generate_invoice_number(self):
        inv_no = f"INV-{datetime.now().strftime('%m%d%H%M')}"
        self.inv_lbl.text = f"[b]{inv_no}[/b]"

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=6)
        
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
        
        self.inv_lbl = Label(text='[b]INV-001[/b]', markup=True, font_size=12, size_hint_x=None, width=95, halign='left', color=(0.2, 0.9, 0.5, 1))
        self.inv_lbl.bind(size=self.inv_lbl.setter('text_size'))
        top_bar.add_widget(self.inv_lbl)
        
        title_lbl = Label(text='[b]POS COUNTER[/b]', markup=True, font_size=12, halign='center')
        title_lbl.bind(size=title_lbl.setter('text_size'))
        top_bar.add_widget(title_lbl)
        
        self.date_lbl = Label(text='', font_size=11, size_hint_x=None, width=85, halign='right', color=(0.8, 0.8, 0.8, 1))
        self.date_lbl.bind(size=self.date_lbl.setter('text_size'))
        top_bar.add_widget(self.date_lbl)
        main_layout.add_widget(top_bar)
        
        self.mobile_input = TextInput(
            hint_text='Customer Mobile Number', 
            multiline=False, 
            size_hint_y=None, 
            height=38,
            font_size=13
        )
        main_layout.add_widget(self.mobile_input)
        
        search_box = BoxLayout(size_hint_y=None, height=40, spacing=6)
        self.search_input = TextInput(
            hint_text='Search item or scan barcode...', 
            multiline=False, 
            font_size=13
        )
        self.search_input.bind(text=self.on_search_text_changed)
        self.search_input.bind(on_text_validate=self.add_first_suggestion)
        search_box.add_widget(self.search_input)
        
        btn_scan = Button(
            text='📷 SCAN', 
            size_hint_x=None, 
            width=75,
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=12
        )
        btn_scan.bind(on_press=self.open_mobile_scanner)
        search_box.add_widget(btn_scan)
        main_layout.add_widget(search_box)
        
        self.suggestions_scroll = ScrollView(size_hint_y=None, height=0)
        self.suggestions_layout = GridLayout(cols=1, spacing=2, size_hint_y=None)
        self.suggestions_layout.bind(minimum_height=self.suggestions_layout.setter('height'))
        self.suggestions_scroll.add_widget(self.suggestions_layout)
        main_layout.add_widget(self.suggestions_scroll)
        
        header_layout = BoxLayout(size_hint_y=None, height=28, spacing=4)
        header_layout.add_widget(Label(text='[b]Item Name[/b]', markup=True, font_size=12, halign='left'))
        header_layout.add_widget(Label(text='[b]Rate[/b]', markup=True, font_size=12, size_hint_x=None, width=55, halign='center'))
        header_layout.add_widget(Label(text='[b]Qty / Controls[/b]', markup=True, font_size=12, size_hint_x=None, width=110, halign='center'))
        header_layout.add_widget(Label(text='[b]Total[/b]', markup=True, font_size=12, size_hint_x=None, width=65, halign='right'))
        main_layout.add_widget(header_layout)
        
        self.cart_layout = GridLayout(cols=1, spacing=4, size_hint_y=None)
        self.cart_layout.bind(minimum_height=self.cart_layout.setter('height'))
        
        cart_scroll = ScrollView(size_hint_y=1)
        cart_scroll.add_widget(self.cart_layout)
        main_layout.add_widget(cart_scroll)
        
        footer_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=175, spacing=5)
        
        pay_row = BoxLayout(size_hint_y=None, height=34, spacing=4)
        pay_row.add_widget(Label(text='[b]Pay:[/b]', markup=True, font_size=12, size_hint_x=None, width=45))
        
        self.btn_cash = Button(text='CASH', font_size=12, bold=True)
        self.btn_cash.bind(on_press=lambda x: self.set_payment_mode("CASH"))
        pay_row.add_widget(self.btn_cash)
        
        self.btn_upi = Button(text='UPI', font_size=12, bold=True)
        self.btn_upi.bind(on_press=lambda x: self.set_payment_mode("UPI"))
        pay_row.add_widget(self.btn_upi)
        
        self.btn_card = Button(text='CARD', font_size=12, bold=True)
        self.btn_card.bind(on_press=lambda x: self.set_payment_mode("CARD"))
        pay_row.add_widget(self.btn_card)
        
        self.btn_mixed = Button(text='MIXED', font_size=12, bold=True)
        self.btn_mixed.bind(on_press=lambda x: self.open_mixed_payment_popup())
        pay_row.add_widget(self.btn_mixed)
        
        footer_layout.add_widget(pay_row)
        
        bottom_row = BoxLayout(size_hint_y=None, height=32, spacing=4)
        bottom_row.add_widget(Label(text='Disc%:', font_size=12, size_hint_x=None, width=45, bold=True))
        
        self.disc_input = TextInput(text='0', multiline=False, font_size=12, size_hint_x=None, width=45)
        self.disc_input.bind(text=lambda x, y: self.refresh_cart_display())
        bottom_row.add_widget(self.disc_input)
        
        self.total_lbl = Label(
            text='Sub:₹0 | D:₹0 | Tot:₹0', 
            font_size=12, 
            bold=True,
            size_hint_x=1,
            halign='right',
            color=(1, 0.9, 0.4, 1)
        )
        self.total_lbl.bind(size=self.total_lbl.setter('text_size'))
        bottom_row.add_widget(self.total_lbl)
        footer_layout.add_widget(bottom_row)
        
        btn_save = Button(
            text='🖨️ PRINT & SAVE BILL', 
            size_hint_y=None, 
            height=42,
            background_color=(0.1, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=13
        )
        btn_save.bind(on_press=self.show_bill_preview)
        footer_layout.add_widget(btn_save)
        
        btn_delete = Button(
            text='🗑️ DELETE SELECTED ITEM', 
            size_hint_y=None, 
            height=36,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=12
        )
        btn_delete.bind(on_press=self.delete_selected_item)
        footer_layout.add_widget(btn_delete)
        
        main_layout.add_widget(footer_layout)
        self.add_widget(main_layout)
        self.update_payment_buttons_visual()

    def open_mobile_scanner(self, instance):
        # Mobile camera barcode scanner trigger for Android APK build
        self.total_lbl.text = "Camera scanner ready for mobile"
        # Yahan aap pyzbar ya Android Intent Zxing integration add kar sakte hain jab APK banayein

    def set_payment_mode(self, mode):
        self.selected_payment_mode = mode
        self.split_amounts = {"CASH": 0.0, "UPI": 0.0, "CARD": 0.0}
        self.update_payment_buttons_visual()

    def update_payment_buttons_visual(self):
        active_color = (0.1, 0.5, 0.2, 1)
        inactive_color = (0.3, 0.3, 0.3, 1)
        
        self.btn_cash.background_color = active_color if self.selected_payment_mode == "CASH" else inactive_color
        self.btn_upi.background_color = active_color if self.selected_payment_mode == "UPI" else inactive_color
        self.btn_card.background_color = active_color if self.selected_payment_mode == "CARD" else inactive_color
        self.btn_mixed.background_color = active_color if self.selected_payment_mode == "MIXED" else inactive_color

    def open_mixed_payment_popup(self):
        grand_total = self.get_grand_total()
        if grand_total <= 0:
            self.total_lbl.text = 'Add items first!'
            return

        popup_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        popup_layout.add_widget(Label(text=f"[b]Grand Total: ₹{grand_total:.2f}[/b]", markup=True, font_size=14, size_hint_y=None, height=30))

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        
        grid.add_widget(Label(text='Cash Amount:', font_size=13, halign='left'))
        cash_input = TextInput(text=str(grand_total), multiline=False, font_size=13)
        grid.add_widget(cash_input)

        grid.add_widget(Label(text='UPI Amount:', font_size=13, halign='left'))
        upi_input = TextInput(text="0.0", multiline=False, font_size=13)
        grid.add_widget(upi_input)

        grid.add_widget(Label(text='Card Amount:', font_size=13, halign='left'))
        card_input = TextInput(text="0.0", multiline=False, font_size=13)
        grid.add_widget(card_input)

        popup_layout.add_widget(grid)

        err_lbl = Label(text='', color=(1, 0.4, 0.4, 1), font_size=12, size_hint_y=None, height=25)
        popup_layout.add_widget(err_lbl)

        btn_box = BoxLayout(size_hint_y=None, height=45, spacing=10)
        btn_apply = Button(text='Apply Split', background_color=(0.1, 0.6, 0.2, 1), bold=True)
        btn_close = Button(text='Cancel', background_color=(0.7, 0.2, 0.2, 1), bold=True)
        
        btn_box.add_widget(btn_apply)
        btn_box.add_widget(btn_close)
        popup_layout.add_widget(btn_box)

        popup = Popup(title='Split Payment (Mixed)', content=popup_layout, size_hint=(0.85, 0.65))
        self._updating_split = False

        def recalculate_split(source_changed):
            if self._updating_split:
                return
            self._updating_split = True
            try:
                c = float(cash_input.text.strip()) if cash_input.text.strip() != "" else 0.0
                u = float(upi_input.text.strip()) if upi_input.text.strip() != "" else 0.0
                ca = float(card_input.text.strip()) if card_input.text.strip() != "" else 0.0

                if source_changed == 'CASH':
                    rem = grand_total - c
                    if rem >= 0:
                        u = rem
                        ca = 0.0
                    else:
                        c = grand_total
                        u = 0.0
                        ca = 0.0
                    upi_input.text = f"{u:.2f}"
                    card_input.text = f"{ca:.2f}"
                elif source_changed == 'UPI':
                    rem_after_cash = grand_total - c
                    if u <= rem_after_cash:
                        ca = rem_after_cash - u
                    else:
                        u = rem_after_cash
                        ca = 0.0
                    card_input.text = f"{ca:.2f}"
                elif source_changed == 'CARD':
                    rem_after_cash = grand_total - c
                    if ca <= rem_after_cash:
                        u = rem_after_cash - ca
                    else:
                        ca = rem_after_cash
                        u = 0.0
                    upi_input.text = f"{u:.2f}"
            except Exception:
                pass
            self._updating_split = False

        cash_input.bind(text=lambda instance, value: recalculate_split('CASH'))
        upi_input.bind(text=lambda instance, value: recalculate_split('UPI'))
        card_input.bind(text=lambda instance, value: recalculate_split('CARD'))

        def open_callback(instance):
            cash_input.focus = True
            cash_input.select_all()
        popup.bind(on_open=open_callback)

        def apply_split(instance):
            try:
                c = float(cash_input.text.strip() or 0)
                u = float(upi_input.text.strip() or 0)
                ca = float(card_input.text.strip() or 0)
                
                if abs((c + u + ca) - grand_total) > 0.5:
                    err_lbl.text = f"Error: Total split (₹{c+u+ca}) must equal Grand Total (₹{grand_total})"
                    return

                self.split_amounts = {"CASH": c, "UPI": u, "CARD": ca}
                self.selected_payment_mode = "MIXED"
                self.update_payment_buttons_visual()
                popup.dismiss()
            except Exception as e:
                err_lbl.text = "Please enter valid numbers!"

        btn_apply.bind(on_press=apply_split)
        btn_close.bind(on_press=popup.dismiss)
        popup.open()

    def get_grand_total(self):
        subtotal = sum(item['rate'] * item['qty'] for item in self.cart_items)
        try:
            disc_pct = float(self.disc_input.text.strip())
        except:
            disc_pct = 0.0
        discount_amount = (subtotal * disc_pct) / 100.0
        return subtotal - discount_amount

    def on_search_text_changed(self, instance, value):
        self.suggestions_layout.clear_widgets()
        if not value.strip():
            self.suggestions_scroll.height = 0
            return
            
        suggestions = search_items_suggestions(value)
        if suggestions:
            self.suggestions_scroll.height = min(len(suggestions) * 32, 120)
            for item in suggestions:
                name, rate, stock = item
                btn = Button(
                    text=f"{name} (Stk: {int(stock)}) - ₹{rate}",
                    size_hint_y=None,
                    height=30,
                    background_color=(0.2, 0.2, 0.2, 1),
                    color=(1, 1, 1, 1),
                    halign='left',
                    font_size=12
                )
                btn.bind(size=btn.setter('text_size'))
                btn.bind(on_press=lambda x, n=name, r=rate: self.select_item_from_suggestion(n, r))
                self.suggestions_layout.add_widget(btn)
        else:
            self.suggestions_scroll.height = 0

    def select_item_from_suggestion(self, name, rate):
        self.add_to_cart_direct(name, float(rate))
        self.search_input.text = ''
        self.suggestions_scroll.height = 0

    def add_first_suggestion(self, instance):
        query = self.search_input.text.strip()
        if not query:
            return
        item = search_item(query)
        if item:
            name, rate, stock = item
            self.add_to_cart_direct(name, float(rate))
            self.search_input.text = ''
            self.suggestions_scroll.height = 0
        else:
            suggestions = search_items_suggestions(query)
            if suggestions:
                name, rate, stock = suggestions[0]
                self.add_to_cart_direct(name, float(rate))
                self.search_input.text = ''
                self.suggestions_scroll.height = 0

    def add_to_cart_direct(self, name, rate):
        found = False
        for cart_item in self.cart_items:
            if cart_item['name'] == name:
                cart_item['qty'] += 1
                found = True
                break
        
        if not found:
            self.cart_items.append({
                'name': name,
                'rate': rate,
                'qty': 1.0
            })
        self.selected_item_name = name
        self.refresh_cart_display()

    def update_qty(self, item_name, change):
        for cart_item in self.cart_items:
            if cart_item['name'] == item_name:
                cart_item['qty'] += change
                if cart_item['qty'] <= 0:
                    self.cart_items.remove(cart_item)
                    if self.selected_item_name == item_name:
                        self.selected_item_name = None
                break
        self.refresh_cart_display()

    def select_row_item(self, item_name):
        self.selected_item_name = item_name
        self.refresh_cart_display()

    def delete_selected_item(self, instance):
        if not self.selected_item_name:
            self.total_lbl.text = 'Select item!'
            return
        self.cart_items = [item for item in self.cart_items if item['name'] != self.selected_item_name]
        self.selected_item_name = None
        self.refresh_cart_display()

    def refresh_cart_display(self):
        self.cart_layout.clear_widgets()
        subtotal = 0.0
        
        for item in self.cart_items:
            is_selected = (item['name'] == self.selected_item_name)
            
            row = BoxLayout(size_hint_y=None, height=40, spacing=4, padding=2)
            
            with row.canvas.before:
                if is_selected:
                    Color(0.25, 0.45, 0.7, 1)
                else:
                    Color(0.18, 0.18, 0.18, 1)
                row.rect = Rectangle(pos=row.pos, size=row.size)
            
            def update_row_bg(instance, value):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    if is_selected:
                        Color(0.25, 0.45, 0.7, 1)
                    else:
                        Color(0.18, 0.18, 0.18, 1)
                    Rectangle(pos=instance.pos, size=instance.size)
            row.bind(pos=update_row_bg, size=update_row_bg)
            
            name_btn = Button(
                text=item['name'], 
                font_size=11, 
                halign='left', 
                valign='middle',
                background_color=(0, 0, 0, 0),
                color=(1, 1, 1, 1)
            )
            name_btn.bind(size=name_btn.setter('text_size'))
            name_btn.bind(on_press=lambda x, n=item['name']: self.select_row_item(n))
            row.add_widget(name_btn)
            
            total_price = item['rate'] * item['qty']
            subtotal += total_price
            
            row.add_widget(Label(text=f"₹{item['rate']:.0f}", font_size=11, size_hint_x=None, width=55, halign='center'))
            
            qty_box = BoxLayout(size_hint_x=None, width=110, spacing=2)
            
            btn_minus = Button(text='-', font_size=13, bold=True, background_color=(0.7, 0.3, 0.3, 1))
            btn_minus.bind(on_press=lambda x, n=item['name']: self.update_qty(n, -1))
            qty_box.add_widget(btn_minus)
            
            qty_lbl = Label(text=str(int(item['qty'])), font_size=12, halign='center', bold=True)
            qty_box.add_widget(qty_lbl)
            
            btn_plus = Button(text='+', font_size=13, bold=True, background_color=(0.2, 0.5, 0.3, 1))
            btn_plus.bind(on_press=lambda x, n=item['name']: self.update_qty(n, 1))
            qty_box.add_widget(btn_plus)
            
            row.add_widget(qty_box)
            row.add_widget(Label(text=f"₹{total_price:.0f}", font_size=12, size_hint_x=None, width=65, halign='right', bold=True, color=(1, 0.9, 0.5, 1)))
            
            self.cart_layout.add_widget(row)
            
        try:
            disc_pct = float(self.disc_input.text.strip())
        except:
            disc_pct = 0.0
            
        discount_amount = (subtotal * disc_pct) / 100.0
        grand_total = subtotal - discount_amount
        
        self.total_lbl.text = f"Sub:₹{subtotal:.0f} | D:₹{discount_amount:.0f} | Tot:₹{grand_total:.0f}"

    def show_bill_preview(self, instance):
        if not self.cart_items:
            self.total_lbl.text = 'Cart is Empty!'
            return
            
        mobile = self.mobile_input.text.strip()
        if not mobile:
            mobile = 'Walk-in'
            
        invoice_no = self.inv_lbl.text.replace('[b]', '').replace('[/b]', '')
        date_str = self.date_lbl.text
        
        if self.selected_payment_mode == "MIXED":
            payment_str = f"MIXED (Cash:₹{self.split_amounts['CASH']}, UPI:₹{self.split_amounts['UPI']}, Card:₹{self.split_amounts['CARD']})"
        else:
            payment_str = self.selected_payment_mode
        
        subtotal = sum(item['rate'] * item['qty'] for item in self.cart_items)
        try:
            disc_pct = float(self.disc_input.text.strip())
        except:
            disc_pct = 0.0
        discount_amount = (subtotal * disc_pct) / 100.0
        grand_total = subtotal - discount_amount
        
        preview_text = generate_bill_receipt_text(
            invoice_no, date_str, mobile, self.cart_items, 
            subtotal, disc_pct, discount_amount, grand_total, payment_str
        )
        
        popup_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        scroll = ScrollView(size_hint=(1, 1))
        preview_lbl = Label(
            text=preview_text,
            font_size=12,
            halign='left',
            valign='top',
            size_hint_y=None,
            color=(0.9, 0.9, 0.9, 1)
        )
        preview_lbl.bind(texture_size=lambda s, w: setattr(s, 'height', w[1]))
        preview_lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        scroll.add_widget(preview_lbl)
        popup_layout.add_widget(scroll)
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        
        btn_confirm = Button(
            text='🖨️ CONFIRM & PRINT',
            background_color=(0.1, 0.6, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=12
        )
        
        btn_cancel = Button(
            text='❌ CLOSE',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=12
        )
        
        btn_layout.add_widget(btn_confirm)
        btn_layout.add_widget(btn_cancel)
        popup_layout.add_widget(btn_layout)
        
        self.preview_popup = Popup(
            title='Bill Format Preview',
            content=popup_layout,
            size_hint=(0.95, 0.9)
        )
        
        btn_cancel.bind(on_press=self.preview_popup.dismiss)
        btn_confirm.bind(on_press=lambda x: self.confirm_and_print(mobile, grand_total, payment_str))
        
        self.preview_popup.open()

    def confirm_and_print(self, mobile, grand_total, payment_mode):
        success, msg = save_bill_to_db(mobile, self.cart_items, grand_total, payment_mode)
        if success:
            self.preview_popup.dismiss()
            self.cart_items = []
            self.selected_item_name = None
            self.disc_input.text = '0'
            self.split_amounts = {"CASH": 0.0, "UPI": 0.0, "CARD": 0.0}
            self.refresh_cart_display()
            self.mobile_input.text = ''
            self.generate_invoice_number()
            self.total_lbl.text = 'Printed & Saved Successfully!'
        else:
            self.total_lbl.text = f'Error: {msg}'