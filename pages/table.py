import customtkinter as ctk
import state
import utils
import tkinter as tk

class TablePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(header, text="Premier League", font=("Arial", 16), text_color="white").pack()
        ctk.CTkLabel(header, text="Table", font=("Arial", 20, "bold"), text_color=state.ACCENT).pack()

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", pady=10)

        try:
            if state.my_cursor:
                state.my_cursor.execute("SELECT DISTINCT season_year FROM Matches ORDER BY season_year DESC")
                seasons = [str(r[0]) for r in state.my_cursor.fetchall()]
            else:
                seasons = ["2024"]
        except Exception:
            seasons = ["2024"]
            
        if "2025" not in seasons:
            seasons.insert(0, "2025")

        self.season_var = tk.StringVar(value="2025" if "2025" in seasons else (seasons[0] if seasons else "2024"))
        season_box = ctk.CTkFrame(controls, fg_color="#0f1b2e", corner_radius=12)
        season_box.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(season_box, text="Season", text_color="gray").pack(anchor="w", padx=10, pady=(5, 0))
        season_menu = ctk.CTkOptionMenu(season_box, values=seasons, variable=self.season_var, fg_color="#0f1b2e", button_color=state.ACCENT, command=lambda _: self.refresh_table())
        season_menu.pack(fill="x", padx=5, pady=5)

        self.sort_var = tk.StringVar(value="Pts")
        sort_box = ctk.CTkFrame(controls, fg_color="#0f1b2e", corner_radius=12)
        sort_box.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(sort_box, text="Sort By", text_color="gray").pack(anchor="w", padx=10, pady=(5, 0))
        sort_menu = ctk.CTkOptionMenu(sort_box, values=["Pts", "GD", "W"], variable=self.sort_var, fg_color="#0f1b2e", button_color=state.ACCENT, command=lambda _: self.refresh_table())
        sort_menu.pack(fill="x", padx=5, pady=5)

        card = ctk.CTkFrame(self, fg_color="#0f1b2e", corner_radius=15)
        card.pack(fill="both", expand=True, pady=10)

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", pady=5)

        header_config = [
            ("#", 30),        
            ("Team", 130),    
            ("P", 35),        
            ("W", 30),        
            ("D", 30),        
            ("L", 30),        
            ("GD", 35),       
            ("Pts", 40)       
        ]

        for text, w in header_config:
            color = state.ACCENT if text == "Pts" else "white"
            align = "w" if text == "Team" else "center"
            ctk.CTkLabel(header_row, text=text, width=w, text_color=color, 
                         font=("Arial", 11, "bold"), anchor=align).pack(side="left", padx=1)
                         
        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.refresh_table()

    def load_standings(self, season):
        if str(season) == "2025":
            return utils.get_2025_standings()

        query = """
                SELECT t.TeamName, t.teamLogo, COUNT(*) AS P,
                SUM(CASE WHEN GoalsFor > GoalsAgainst THEN 1 ELSE 0 END) AS W,
                SUM(CASE WHEN GoalsFor = GoalsAgainst THEN 1 ELSE 0 END) AS D,
                SUM(CASE WHEN GoalsFor < GoalsAgainst THEN 1 ELSE 0 END) AS L,
                SUM(GoalsFor - GoalsAgainst) AS GD,
                SUM(CASE WHEN GoalsFor > GoalsAgainst THEN 3 WHEN GoalsFor = GoalsAgainst THEN 1 ELSE 0 END) AS Pts
                FROM (
                    SELECT hometeamID AS TeamID, home_goals AS GoalsFor, away_goals AS GoalsAgainst FROM Matches WHERE season_year = ?
                    UNION ALL
                    SELECT awayteamID AS TeamID, away_goals AS GoalsFor, home_goals AS GoalsAgainst FROM Matches WHERE season_year = ?
                ) AS AllMatches
                JOIN Teams t ON AllMatches.TeamID = t.teamID
                GROUP BY t.TeamName, t.teamLogo
        """
        try:
            if state.my_cursor:
                state.my_cursor.execute(query, (season, season))
                return state.my_cursor.fetchall()
            return []
        except Exception: 
            return []

    def refresh_table(self):
        for w in self.scroll.winfo_children(): 
            w.destroy()
            
        data = self.load_standings(self.season_var.get())
        
        # Determine sorting based on self.sort_var
        sort_by = self.sort_var.get()
        if sort_by == "Pts":
            data.sort(key=lambda x: x[7], reverse=True)
        elif sort_by == "GD":
            data.sort(key=lambda x: x[6], reverse=True)
        elif sort_by == "W":
            data.sort(key=lambda x: x[3], reverse=True)

        for i, row in enumerate(data, 1):
            team_name, logo_path = row[0], row[1]
            bg_color = "#0b3d2e" if i <= 4 else ("#3d0b0b" if i > len(data)-3 else "#0f1b2e")
            
            row_frame = ctk.CTkFrame(self.scroll, fg_color=bg_color, corner_radius=6, height=35)
            row_frame.pack(fill="x", pady=1, padx=2)
            row_frame.pack_propagate(False) 

            ctk.CTkLabel(row_frame, text=str(i), width=30, font=("Arial", 11)).pack(side="left")

            team_info = ctk.CTkFrame(row_frame, fg_color="transparent", width=130, height=35)
            team_info.pack(side="left", padx=1)
            team_info.pack_propagate(False)
            
            t_logo = utils.load_image_safe(logo_path, size=(25, 25))
            if t_logo: 
                ctk.CTkLabel(team_info, image=t_logo, text="").pack(side="left", padx=(2, 5))
            
            ctk.CTkLabel(team_info, text=team_name, font=("Arial", 11), anchor="w").pack(side="left")

            values = row[2:] 
            widths = [35, 30, 30, 30, 35, 40] 
            for j, val in enumerate(values):
                color = state.ACCENT if j == 5 else "white" 
                ctk.CTkLabel(row_frame, text=str(val), width=widths[j], 
                             text_color=color, font=("Arial", 11)).pack(side="left", padx=1)
