import threading
import customtkinter as ctk
import state
import utils

class MatchesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        ctk.CTkLabel(self, text="Match Results", font=("Arial", 22, "bold"), text_color=state.ACCENT).pack(pady=(5, 10))

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=5)

        self.season_var = ctk.StringVar(value="2025")
        self.season_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["2020", "2021", "2022", "2023", "2024", "2025"],
            variable=self.season_var,
            width=110,
            fg_color="#1E293B",
            button_color=state.ACCENT,
            command=self.load_data_from_db
        )
        self.season_menu.pack(side="left", padx=10)

        self.week_var = ctk.StringVar(value="Week 1")
        self.week_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=[f"Week {i}" for i in range(1, 39)],
            variable=self.week_var,
            width=110,
            fg_color="#1E293B",
            button_color=state.ACCENT,
            command=self.load_data_from_db
        )
        self.week_menu.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.pack(pady=(4, 0))

        self.simulate_btn = ctk.CTkButton(
            self,
            text="Simulate Week",
            fg_color=state.ACCENT,
            height=38,
            command=self.simulate_selected_week
        )
        self.simulate_btn.pack(pady=8, fill="x", padx=20)

        self.results_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_scroll.pack(fill="both", expand=True, pady=10)

        self.load_data_from_db()

    def simulate_selected_week(self):
        if not state.generated_fixtures:
            self.status_label.configure(text="Generate fixtures from the Fixture page first.", text_color="red")
            return

        selected_week = int(self.week_var.get().split(" ")[1])

        if selected_week > 1 and (selected_week - 1) not in state.simulated_2025_results:
            self.status_label.configure(text=f"Please simulate Week {selected_week - 1} first!", text_color="red")
            return

        self.status_label.configure(text="Simulating week... Please wait.", text_color="gray")

        def background_task():
            try:
                utils.simulate_2025_week(selected_week)
                def on_success():
                    self.status_label.configure(text=f"Week {selected_week} simulated and table updated.", text_color=state.ACCENT)
                    self.load_data_from_db()
                self.after(0, on_success)
            except Exception as e:
                def on_error():
                    self.status_label.configure(text=f"Simulation error: {e}", text_color="red")
                self.after(0, on_error)

        threading.Thread(target=background_task, daemon=True).start()

    def render_match_card(self, home_n, home_logo_path, home_g, away_g, away_n, away_logo_path, probs=None):
        card = ctk.CTkFrame(self.results_scroll, fg_color="#1E293B", corner_radius=10)
        card.pack(fill="x", pady=6, padx=5)

        home_frame = ctk.CTkFrame(card, fg_color="transparent")
        home_frame.pack(side="left", expand=True, fill="x")

        home_row = ctk.CTkFrame(home_frame, fg_color="transparent")
        home_row.pack(anchor="e", fill="x")
        h_logo = utils.load_image_safe(home_logo_path, size=(40, 40))
        if h_logo:
            ctk.CTkLabel(home_row, image=h_logo, text="").pack(side="right", padx=5)
        ctk.CTkLabel(home_row, text=home_n, font=("Arial", 12, "bold"), anchor="e").pack(side="right", padx=5)
        if probs:
            ctk.CTkLabel(
                home_frame,
                text=f"Win {probs[0] * 100:.1f}%",
                text_color="#4ade80",
                font=("Arial", 11, "bold"),
                anchor="e"
            ).pack(anchor="e", padx=8, pady=(2, 0))

        score_text = "TBD" if home_g is None or away_g is None else f"{home_g} - {away_g}"
        score_bg = ctk.CTkFrame(card, fg_color=state.PRIMARY_BG, corner_radius=5, width=82, height=54)
        score_bg.pack(side="left", padx=10, pady=10)
        score_bg.pack_propagate(False)
        ctk.CTkLabel(score_bg, text=score_text, font=("Arial", 14, "bold"), text_color=state.ACCENT).pack(expand=True)
        if probs:
            ctk.CTkLabel(
                score_bg,
                text=f"Draw {probs[1] * 100:.1f}%",
                text_color="#facc15",
                font=("Arial", 9, "bold")
            ).pack(pady=(0, 3))

        away_frame = ctk.CTkFrame(card, fg_color="transparent")
        away_frame.pack(side="left", expand=True, fill="x")

        away_row = ctk.CTkFrame(away_frame, fg_color="transparent")
        away_row.pack(anchor="w", fill="x")
        a_logo = utils.load_image_safe(away_logo_path, size=(40, 40))
        if a_logo:
            ctk.CTkLabel(away_row, image=a_logo, text="").pack(side="left", padx=5)
        ctk.CTkLabel(away_row, text=away_n, font=("Arial", 12, "bold"), anchor="w").pack(side="left", padx=5)
        if probs:
            ctk.CTkLabel(
                away_frame,
                text=f"Win {probs[2] * 100:.1f}%",
                text_color="#38bdf8",
                font=("Arial", 11, "bold"),
                anchor="w"
            ).pack(anchor="w", padx=8, pady=(2, 0))

    def load_data_from_db(self, *args):
        for child in self.results_scroll.winfo_children():
            child.destroy()

        selected_season = self.season_var.get()
        selected_week = int(self.week_var.get().split(" ")[1])

        if selected_season == "2025":
            self.simulate_btn.configure(state="normal" if state.generated_fixtures else "disabled")
            logo_map = utils.get_team_logo_map()
            matches = utils.get_2025_matches_for_display(selected_week)

            if not matches:
                ctk.CTkLabel(
                    self.results_scroll,
                    text="Generate the 2025 fixtures from the Fixture page first.",
                    text_color="gray"
                ).pack(pady=20)
                return

            for match in matches:
                probs = None
                if match["home_prob"] is not None:
                    probs = (match["home_prob"], match["draw_prob"], match["away_prob"])
                self.render_match_card(
                    match["home"], logo_map.get(match["home"]),
                    match["home_goals"], match["away_goals"],
                    match["away"], logo_map.get(match["away"]), probs
                )
            return

        self.simulate_btn.configure(state="disabled")

        try:
            if not state.my_cursor:
                ctk.CTkLabel(self.results_scroll, text="Database Connection Error", text_color="red").pack(pady=20)
                return
                
            query = """
            SELECT t1.teamname, t1.teamLogo, m.home_goals, m.away_goals, t2.teamname, t2.teamLogo
            FROM Matches m
            JOIN Teams t1 ON m.hometeamID = t1.teamID
            JOIN Teams t2 ON m.awayteamID = t2.teamID
            WHERE m.season_year = ? AND m.matchweek = ?
            """
            state.my_cursor.execute(query, (selected_season, selected_week))
            matches = state.my_cursor.fetchall()

            if not matches:
                ctk.CTkLabel(self.results_scroll, text="No matches found for this selection.", text_color="gray").pack(pady=20)
                return

            for row in matches:
                home_n, home_logo_path, home_g, away_g, away_n, away_logo_path = row
                self.render_match_card(home_n, home_logo_path, home_g, away_g, away_n, away_logo_path)

        except Exception as e:
            print(f"Error fetching matches: {e}")
            ctk.CTkLabel(self.results_scroll, text="Database Connection Error", text_color="red").pack(pady=20)
