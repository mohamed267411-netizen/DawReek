import customtkinter as ctk
import state

# Import all pages
from pages.intro import IntroPage
from pages.auth import LoginPage, ForgotPasswordPage, NewPasswordPage, PasswordSuccessPage, SignupPage
from pages.team_selection import TeamSelectionPage, SavedTeamsPage
from pages.home import HomePage
from pages.matches import MatchesPage
from pages.fixtures import FixturesPage
from pages.table import TablePage
from pages.predictions import PredictionsPage

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.geometry("450x700")
        self.title("DawReeK")
        self.configure(fg_color=state.PRIMARY_BG)
        
        self.container = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        self.container.pack(fill="both", expand=True)
        
        self.pages = {}
        self.content_frame = None
        self.nav_frame = None
        
        self.show_page("IntroPage")

    def create_dashboard_layout(self):
        """Creates the main app layout with nav bar if not exists"""
        if self.content_frame and self.nav_frame and self.content_frame.winfo_exists() and self.nav_frame.winfo_exists():
            return
            
        for w in self.container.winfo_children():
            w.destroy()
            
        self.content_frame = ctk.CTkFrame(self.container, fg_color=state.PRIMARY_BG)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.nav_frame = ctk.CTkFrame(self.container, fg_color="#0B1220", height=70)
        self.nav_frame.pack(side="bottom", fill="x")

    def show_page(self, page_name):
        dashboard_pages = ["HomePage", "MatchesPage", "FixturesPage", "TablePage", "PredictionsPage"]
        
        if page_name in dashboard_pages:
            self.create_dashboard_layout()
            
            for w in self.content_frame.winfo_children():
                w.pack_forget()
                
            if page_name not in self.pages or getattr(self.pages[page_name], "master", None) != self.content_frame:
                page_class = globals()[page_name]
                self.pages[page_name] = page_class(self.content_frame, self)
                
            page = self.pages[page_name]
            page.pack(fill="both", expand=True)
            
            # Refresh specific pages if needed
            if hasattr(page, 'load_data_from_db'):
                page.load_data_from_db()
            if hasattr(page, 'refresh_table'):
                page.refresh_table()
                
            self.create_bottom_nav(page_name)
        else:
            self.content_frame = None
            self.nav_frame = None
            
            for w in self.container.winfo_children():
                w.pack_forget()
                
            if page_name not in self.pages or getattr(self.pages[page_name], "master", None) != self.container:
                page_class = globals()[page_name]
                self.pages[page_name] = page_class(self.container, self)
                
            page = self.pages[page_name]
            page.pack(fill="both", expand=True)

    def get_page(self, page_name):
        if page_name not in self.pages:
            page_class = globals()[page_name]
            self.pages[page_name] = page_class(self.container, self)
        return self.pages[page_name]

    def create_bottom_nav(self, active_page="HomePage"):
        if not self.nav_frame:
            return  
            
        for w in self.nav_frame.winfo_children():
            w.destroy()

        self.nav_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        icons = {
            "HomePage": ("📊", "Analysis"),
            "MatchesPage": ("⚽", "Matches"),
            "FixturesPage": ("📊", "Fixture"),
            "TablePage": ("📋", "Table"),
            "PredictionsPage": ("🎯", "Predictions")
        }

        col = 0
        for key, (icon, text) in icons.items():
            f = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
            f.grid(row=0, column=col, pady=6)

            ctk.CTkFrame(
                f, width=30, height=3,
                fg_color=state.ACCENT if key == active_page else "transparent"
            ).pack(pady=(0,3))

            ctk.CTkButton(
                f,
                text=f"{icon}\n{text}",  
                fg_color="transparent",
                text_color=state.ACCENT if key == active_page else "#9CA3AF",
                hover=True,
                command=lambda k=key: self.show_page(k),
                font=("Arial", 11)
            ).pack()
            col += 1

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
