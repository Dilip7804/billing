# report_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from datetime import datetime
from database import get_sales_reports

class CalendarPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = "Select Date (DD-MM-YYYY)"
        self.size_hint = (0.85, 0.6)
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Aaj ki date ya current month ka layout
        now = datetime.now()
        self.curr_month = now.month
        self.curr_year = now.year
        
        self.month_lbl = Label(text=now.strftime("%B %Y"), font_size=16, bold=True, size_hint_y=None, height=40, color=(0.2, 0.9, 0.5, 1))
        content.add_widget(self.month_lbl)
        
        # Grid for Days (1 to 31)
        self.days_grid = GridLayout(cols=7, spacing=5)
        self.populate_days()
        
        content.add_widget(self.days_grid)
        
        # Close Button
        btn_close = Button(text="Cancel", size_hint_y=None, height=40, background_color=(0.7, 0.2, 0.2, 1))
        btn_close.bind(on_press=self.dismiss)
        content.add_widget(btn_close)
        
        self.content = content

    def populate_days(self):
        self.days_grid.clear_widgets()
        
        # Weekdays header
        days_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for d in days_name:
            self.days_grid.add_widget(Label(text=d, bold=True, font_size=12, color=(0.8, 0.8, 0.8, 1)))
            
        # Sample quick days selector (1 to 31 ke buttons taaki user easily click karke select kar sake)
        for day in range(1, 32):
            # Format day and month with leading zeros
            d_str = f"{day:02d}-{self.curr_month:02d}-{self.curr_year}"
            b = Button(text=str(day), font_size=12, background_color=(0.2, 0.4, 0.6, 1))
            b.bind(on_press=lambda x, date_val=d_str: self.select_date(date_val))
            self.days_grid.add_widget(b)

    def select_date(self, date_str):
        self.callback(date_str)
        self.dismiss()


class ReportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_filter_mode = "ALL"
        self.build_ui()

    def on_enter(self):
        self.load_reports()

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
        
        title_lbl = Label(text='[b]SALES REPORTS[/b]', markup=True, font_size=14, halign='center', color=(0.2, 0.9, 0.5, 1))
        title_lbl.bind(size=title_lbl.setter('text_size'))
        top_bar.add_widget(title_lbl)
        main_layout.add_widget(top_bar)
        
        # Filter Section Box
        filter_box = BoxLayout(orientation='vertical', size_hint_y=None, height=95, spacing=4)
        
        # Row 1: Search Input (Date or Mobile No) + Calendar Button + Search Button
        search_row = BoxLayout(size_hint_y=None, height=36, spacing=6)
        search_row.add_widget(Label(text='Search:', font_size=11, size_hint_x=None, width=55, bold=True))
        
        self.search_input = TextInput(
            hint_text='Date (DD-MM-YYYY) or Mobile No', 
            multiline=False, 
            font_size=12,
            size_hint_x=1
        )
        search_row.add_widget(self.search_input)
        
        # Calendar Popup Trigger Button
        btn_calendar = Button(
            text='📅', 
            size_hint_x=None, 
            width=45,
            background_color=(0.2, 0.6, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=16
        )
        btn_calendar.bind(on_press=self.open_calendar)
        search_row.add_widget(btn_calendar)
        
        btn_search = Button(
            text='🔍 FILTER', 
            size_hint_x=None, 
            width=80,
            background_color=(0.1, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=11
        )
        btn_search.bind(on_press=lambda x: self.load_reports())
        search_row.add_widget(btn_search)
        filter_box.add_widget(search_row)
        
        # Row 2: Payment Mode Filter Buttons
        mode_row = BoxLayout(size_hint_y=None, height=36, spacing=4)
        mode_row.add_widget(Label(text='Mode:', font_size=11, size_hint_x=None, width=45, bold=True))
        
        self.modes = ["ALL", "CASH", "UPI", "CARD", "MIXED"]
        self.mode_buttons = {}
        
        for m in self.modes:
            b = Button(text=m, font_size=11, bold=True)
            b.bind(on_press=lambda x, mode=m: self.set_mode_filter(mode))
            self.mode_buttons[m] = b
            mode_row.add_widget(b)
            
        filter_box.add_widget(mode_row)
        main_layout.add_widget(filter_box)
        
        # Summary Box
        self.summary_lbl = Label(
            text='Total Bills: 0 | Total Collection: ₹0.00',
            font_size=12,
            bold=True,
            size_hint_y=None,
            height=30,
            color=(1, 0.9, 0.4, 1)
        )
        main_layout.add_widget(self.summary_lbl)
        
        # Table Header
        header_layout = BoxLayout(size_hint_y=None, height=28, spacing=2)
        header_layout.add_widget(Label(text='[b]Inv No[/b]', markup=True, font_size=11, size_hint_x=None, width=90, halign='left'))
        header_layout.add_widget(Label(text='[b]Date / Time[/b]', markup=True, font_size=11, size_hint_x=None, width=105, halign='center'))
        header_layout.add_widget(Label(text='[b]Customer[/b]', markup=True, font_size=11, size_hint_x=1, halign='left'))
        header_layout.add_widget(Label(text='[b]Mode[/b]', markup=True, font_size=11, size_hint_x=None, width=65, halign='center'))
        header_layout.add_widget(Label(text='[b]Amount[/b]', markup=True, font_size=11, size_hint_x=None, width=75, halign='right'))
        main_layout.add_widget(header_layout)
        
        # Reports List ScrollView
        self.reports_layout = GridLayout(cols=1, spacing=3, size_hint_y=None)
        self.reports_layout.bind(minimum_height=self.reports_layout.setter('height'))
        
        reports_scroll = ScrollView(size_hint_y=1)
        reports_scroll.add_widget(self.reports_layout)
        main_layout.add_widget(reports_scroll)
        
        self.add_widget(main_layout)
        self.update_mode_buttons_visual()

    def open_calendar(self, instance):
        popup = CalendarPopup(callback=self.on_date_selected)
        popup.open()

    def on_date_selected(self, date_str):
        self.search_input.text = date_str
        self.load_reports()

    def set_mode_filter(self, mode):
        self.selected_filter_mode = mode
        self.update_mode_buttons_visual()
        self.load_reports()

    def update_mode_buttons_visual(self):
        active_color = (0.1, 0.5, 0.2, 1)
        inactive_color = (0.3, 0.3, 0.3, 1)
        for m, btn in self.mode_buttons.items():
            if m == self.selected_filter_mode:
                btn.background_color = active_color
            else:
                btn.background_color = inactive_color

    def load_reports(self):
        self.reports_layout.clear_widgets()
        
        search_query = self.search_input.text.strip().lower()
        
        # Date filter conversion (agar DD-MM-YYYY enter kiya ho)
        date_filter = ""
        if search_query:
            parts = search_query.split('-')
            if len(parts) == 3 and len(parts[0]) <= 2:
                date_filter = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                date_filter = search_query

        bills = get_sales_reports()
        
        total_bills_count = 0
        total_revenue = 0.0
        
        for bill in bills:
            try:
                inv_no = str(bill[0])
                mobile = str(bill[1]) if bill[1] is not None else "Walk-in"
                
                amount = 0.0
                mode = "CASH"
                b_date = ""
                
                for val in bill:
                    if isinstance(val, (int, float)) and val > 10 and val != bill[0]:
                        amount = float(val)
                    elif isinstance(val, str):
                        if "-" in val and ":" in val:
                            b_date = val
                        elif val in ["CASH", "UPI", "CARD", "MIXED"] or "CASH" in val or "UPI" in val:
                            mode = val
                
                if not b_date and len(bill) > 4:
                    b_date = str(bill[-2]) if isinstance(bill[-2], str) else str(bill[4])
                if amount == 0.0:
                    for val in bill:
                        if isinstance(val, (int, float)) and val != bill[0]:
                            amount = float(val)
                            break
                            
            except Exception as e:
                continue
            
            # Search filter check (Date match ya Mobile Number match)
            if search_query:
                match_date = date_filter in b_date.lower()
                match_mobile = search_query in mobile.lower()
                if not (match_date or match_mobile):
                    continue
                
            # Payment mode filter check
            if self.selected_filter_mode != "ALL":
                if self.selected_filter_mode not in mode.upper():
                    continue
            
            total_bills_count += 1
            total_revenue += amount
            
            # Row layout for each bill record
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
            
            row.add_widget(Label(text=f"INV-{inv_no}", font_size=11, size_hint_x=None, width=90, halign='left', color=(0.2, 0.9, 0.5, 1)))
            row.add_widget(Label(text=b_date, font_size=11, size_hint_x=None, width=105, halign='center', color=(0.8, 0.8, 0.8, 1)))
            row.add_widget(Label(text=mobile, font_size=11, size_hint_x=1, halign='left'))
            row.add_widget(Label(text=mode[:6], font_size=10, size_hint_x=None, width=65, halign='center', bold=True, color=(0.4, 0.8, 1, 1)))
            row.add_widget(Label(text=f"₹{amount:.2f}", font_size=11, size_hint_x=None, width=75, halign='right', bold=True, color=(1, 0.9, 0.4, 1)))
            
            self.reports_layout.add_widget(row)
            
        # Update summary text
        self.summary_lbl.text = f"Total Bills: {total_bills_count}  |  Total Collection: ₹{total_revenue:.2f}"