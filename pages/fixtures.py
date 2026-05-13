import customtkinter as ctk
import state
import utils

class FixturesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        ctk.CTkLabel(
            self,
            text="⚽ Premier League Fixtures",
            font=("Arial", 24, "bold"),
            text_color=state.ACCENT
        ).pack(pady=10)

        ctk.CTkLabel(
            self,
            text="2025 Season Official Schedule",
            text_color="gray"
        ).pack()

        ctk.CTkButton(
            self,
            text="Generate Fixtures",
            fg_color=state.ACCENT,
            height=40,
            command=self.generate
        ).pack(pady=10, fill="x", padx=20)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)

        if state.generated_fixtures:
            self.render(state.generated_fixtures)

    def generate(self):
        data = utils.generate_fixtures_with_time()
        self.render(data)

    def render(self, data):
        for w in self.scroll.winfo_children():
            w.destroy()

        for week_idx, week in enumerate(data, start=1):
            week_card = ctk.CTkFrame(self.scroll, fg_color="#0f1b2e", corner_radius=12)
            week_card.pack(fill="x", pady=10)

            ctk.CTkLabel(
                week_card,
                text=f"📅 Week {week_idx}",
                font=("Arial", 18, "bold"),
                text_color=state.ACCENT
            ).pack(anchor="w", padx=10, pady=5)

            for match in week:
                home = match["home"]
                away = match["away"]
                dt = match["datetime"]

                stadium = state.TEAM_STADIUMS.get(home, "Unknown Stadium")

                match_card = ctk.CTkFrame(
                    week_card,
                    fg_color="#1b2a41",
                    corner_radius=10
                )
                match_card.pack(fill="x", padx=10, pady=6)

                ctk.CTkLabel(
                    match_card,
                    text=f"🏟 {stadium}",
                    text_color="lightgray",
                    font=("Arial", 11)
                ).pack(anchor="w", padx=10, pady=2)

                row = ctk.CTkFrame(match_card, fg_color="transparent")
                row.pack(fill="x", padx=10)

                ctk.CTkLabel(
                    row,
                    text=home,
                    font=("Arial", 14, "bold"),
                    text_color="white"
                ).pack(side="left")

                ctk.CTkLabel(
                    row,
                    text="VS",
                    text_color=state.ACCENT,
                    font=("Arial", 12, "bold")
                ).pack(side="left", padx=10)

                ctk.CTkLabel(
                    row,
                    text=away,
                    font=("Arial", 14, "bold"),
                    text_color="white"
                ).pack(side="left")

                ctk.CTkLabel(
                    match_card,
                    text=dt.strftime("%a %d %b    %H:%M"),
                    text_color="gray",
                    font=("Arial", 11)
                ).pack(anchor="e", padx=10, pady=3)
