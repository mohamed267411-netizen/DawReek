import customtkinter as ctk
import state
import utils

class TeamSelectionPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        container = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        container.pack(fill="both", expand=True, padx=16, pady=12)

        frame = ctk.CTkFrame(container, fg_color=state.PRIMARY_BG)
        frame.pack(fill="both", expand=True)

        title = ctk.CTkLabel(frame, text="Choose Your Favorite Team", font=("Arial", 20, "bold"), text_color=state.TEXT_COLOR)
        title.pack(pady=(12,6))

        subtitle = ctk.CTkLabel(frame, text="Select at least one team you support.", font=("Arial", 12), text_color="lightgray")
        subtitle.pack(pady=(0,10))

        grid_container = ctk.CTkFrame(frame, fg_color="transparent")
        grid_container.pack(pady=(6,8), fill="both", expand=True)

        self.teams = list(utils.get_team_logo_map().items())  # Fallback: maybe utils needs to return images. Wait, main.py uses team_logos_images cache directly.
        # Actually in state we didn't store team_logos_images. We should load them here if needed.
        self.team_logos_images = {k: utils.load_image_safe(v, size=(100, 100)) for k, v in state.TEAM_IMAGE_FILES.items()}
        
        self.selected_team = {"name": None}
        self.btn_refs = []

        cols = 3
        row, col = 0, 0
        for name, logo in self.team_logos_images.items():
            if logo:
                btn = ctk.CTkButton(grid_container, image=logo, text=name, compound="top",
                                    fg_color=state.PRIMARY_BG, text_color=state.TEXT_COLOR,
                                    width=110, height=110)
                btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                btn.configure(command=lambda n=name, b=btn: self.choose_team(n, b))
            else:
                btn = ctk.CTkButton(grid_container, text=name, fg_color=state.PRIMARY_BG, text_color=state.TEXT_COLOR,
                                    width=110, height=110, command=lambda n=name: self.choose_team(n, None))
                btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.btn_refs.append(btn)
            col += 1
            if col == cols:
                col = 0
                row += 1

        for c in range(cols):
            grid_container.grid_columnconfigure(c, weight=1)

        self.frame = frame
        
        continue_btn = ctk.CTkButton(frame, text="Continue", command=self.continue_action, fg_color=state.ACCENT)
        continue_btn.pack(pady=12, fill="x")

    def choose_team(self, team, btn):
        self.selected_team["name"] = team
        for b in self.btn_refs:
            try:
                b.configure(fg_color=state.PRIMARY_BG)
            except Exception:
                pass
        if btn:
            btn.configure(fg_color=state.ACCENT)

    def continue_action(self):
        if self.selected_team["name"]:
            if not state.current_user_email:
                notice = ctk.CTkLabel(self.frame, text="You must be logged in to save a team", text_color="red")
                notice.pack(pady=(6,0))
                self.after(2000, notice.destroy)
                return
            try:
                if state.cursor:
                    state.cursor.execute("UPDATE Users SET FavoriteTeam=? WHERE Email=?", (self.selected_team["name"], state.current_user_email))
                    state.conn.commit()
            except Exception:
                err = ctk.CTkLabel(self.frame, text="Could not save to DB, showing confirmation locally", text_color="orange")
                err.pack(pady=(6,0))
                self.after(1500, err.destroy)

            saved_page = self.controller.get_page("SavedTeamsPage")
            saved_page.set_team(self.selected_team["name"], self.team_logos_images.get(self.selected_team["name"]))
            self.controller.show_page("SavedTeamsPage")
        else:
            notice = ctk.CTkLabel(self.frame, text="Please select a team first", text_color="red")
            notice.pack(pady=(6,0))
            self.after(1500, notice.destroy)


class SavedTeamsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        self.frame = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        check_icon = utils.load_image_safe(state.CHECK_ICON_PATH, size=(120, 120))
        if check_icon:
            icon_label = ctk.CTkLabel(self.frame, image=check_icon, text="")
            icon_label.pack(pady=(100, 8))
        else:
            icon_label = ctk.CTkLabel(self.frame, text="✔️", font=("Arial", 48, "bold"), text_color=state.ACCENT)
            icon_label.pack(pady=(100, 8))

        title = ctk.CTkLabel(self.frame, text="You're all set!", font=("Arial", 22, "bold"), text_color=state.TEXT_COLOR)
        title.pack(pady=(6,4))

        subtitle = ctk.CTkLabel(self.frame, text="Your favorite teams are saved.\nLet's start predicting!", font=("Arial", 12), text_color="lightgray", justify="center")
        subtitle.pack(pady=(0,12))

        teams_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        teams_frame.pack(pady=(6,12), fill="x")

        teams_label = ctk.CTkLabel(teams_frame, text="YOUR TEAMS:", font=("Arial", 12, "bold"), text_color=state.TEXT_COLOR)
        teams_label.pack(anchor="w", pady=(0,6))

        self.team_row = ctk.CTkFrame(teams_frame, fg_color="transparent")
        self.team_row.pack(fill="x", pady=(4,6))

        self.logo_label = ctk.CTkLabel(self.team_row, text="")
        self.logo_label.pack(side="left", padx=(0,8))
        
        self.name_label = ctk.CTkLabel(self.team_row, text="", font=("Arial", 14), text_color=state.TEXT_COLOR)
        self.name_label.pack(side="left", anchor="w")

        go_btn = ctk.CTkButton(self.frame, text="Go to Home", command=lambda: self.controller.show_page("HomePage"), fg_color=state.ACCENT)
        go_btn.pack(pady=18, fill="x")

    def set_team(self, name, logo_img):
        if logo_img:
            self.logo_label.configure(image=logo_img)
        self.name_label.configure(text=name)
