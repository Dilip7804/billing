# main.py

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from database import init_db
from login_screen import LoginScreen
from dashboard_screen import DashboardScreen
from billing_screen import BillingScreen
from report_screen import ReportScreen
from stock_screen import StockScreen
from opening_stock_screen import OpeningStockScreen  # Import naya screen

from kivy.core.window import Window
Window.size = (360, 640)

class MeraStoreApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        
        init_db()
        
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(BillingScreen(name='billing'))
        sm.add_widget(ReportScreen(name='report'))
        sm.add_widget(StockScreen(name='stock'))
        sm.add_widget(OpeningStockScreen(name='opening_stock'))  # Add to manager
        
        return sm

if __name__ == '__main__':
    MeraStoreApp().run()