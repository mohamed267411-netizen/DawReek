import customtkinter as ctk
import state
import utils

class IntroPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller
        
        intro_img1 = utils.load_image_safe(state.INTRO_IMG1, size=(300, 300))
        intro_img2 = utils.load_image_safe(state.INTRO_IMG2, size=(260, 300))
        intro_img3 = utils.load_image_safe(state.INTRO_IMG3, size=(260, 300))
        intro_img4 = utils.load_image_safe(state.INTRO_IMG4, size=(260, 300))
        
        self.pages = [
            {"title": "Discover & Predict Matches", "desc": "Predict match results, earn points\nand compete with fans.", "image": intro_img1},
            {"title": "Track Your Performance", "desc": "Check your stats and improve over time.", "image": intro_img2},
            {"title": "Compete with Others", "desc": "Climb the leaderboard and win rewards.", "image": intro_img3},
            {"title": "AI-Powered Predictions", "desc": "Get accurate predictions using AI.", "image": intro_img4},
        ]
        self.current_page = 0
        
        self.image_frame = ctk.CTkFrame(self, height=280, fg_color="transparent")
        self.image_frame.pack(fill="x", pady=(50,10))
        
        self.image_label = ctk.CTkLabel(self.image_frame, text="", corner_radius=50)
        self.image_label.pack(expand=True)
        
        self.title_label = ctk.CTkLabel(self, text="", font=("Arial", 20, "bold"), text_color=state.TEXT_COLOR)
        self.title_label.pack(pady=(10, 5))
        
        self.desc_label = ctk.CTkLabel(self, text="", font=("Arial", 14), justify="center", text_color=state.TEXT_COLOR)
        self.desc_label.pack(pady=5)
        
        self.dots_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dots_frame.pack(pady=10)
        
        self.dot_labels = []
        for i in range(len(self.pages)):
            dot = ctk.CTkLabel(self.dots_frame, text="●", font=("Arial", 14), text_color="gray")
            dot.pack(side="left", padx=3)
            self.dot_labels.append(dot)
            
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=20)
        
        self.next_btn = ctk.CTkButton(self.btn_frame, text="Next", command=self.next_page, fg_color=state.ACCENT)
        self.next_btn.pack(pady=5, fill="x")
        
        self.skip_btn = ctk.CTkButton(self.btn_frame, text="Skip", fg_color="transparent", text_color=state.ACCENT, border_width=2, command=self.skip_intro)
        self.skip_btn.pack()
        
        self.update_page()
        
    def update_page(self):
        page = self.pages[self.current_page]
        self.title_label.configure(text=page["title"])
        self.desc_label.configure(text=page["desc"])
        self.image_label.configure(image=page["image"])
        for i, dot in enumerate(self.dot_labels):
            dot.configure(text_color=state.ACCENT if i == self.current_page else "gray")

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_page()
        else:
            self.controller.show_page("LoginPage")

    def skip_intro(self):
        self.controller.show_page("LoginPage")
