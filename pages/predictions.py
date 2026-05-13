import threading
import customtkinter as ctk
import state
import utils

class PredictionsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        ctk.CTkLabel(
            self,
            text="Match Prediction",
            font=("Arial", 22, "bold"),
            text_color=state.ACCENT
        ).pack(pady=(5, 10))

        teams = utils.get_team_names()
        default_home = teams[0] if teams else "Arsenal"
        default_away = teams[1] if len(teams) > 1 else default_home

        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=4, pady=4)

        teams_box = ctk.CTkFrame(form, fg_color="#0f1b2e", corner_radius=10)
        teams_box.pack(fill="x", pady=6)

        self.home_team_var = ctk.StringVar(value=default_home)
        self.away_team_var = ctk.StringVar(value=default_away)

        ctk.CTkLabel(teams_box, text="Home Team", text_color="gray").pack(anchor="w", padx=12, pady=(10, 2))
        home_menu = ctk.CTkOptionMenu(teams_box, values=teams, variable=self.home_team_var, fg_color="#1E293B", button_color=state.ACCENT)
        home_menu.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(teams_box, text="Away Team", text_color="gray").pack(anchor="w", padx=12, pady=(4, 2))
        away_menu = ctk.CTkOptionMenu(teams_box, values=teams, variable=self.away_team_var, fg_color="#1E293B", button_color=state.ACCENT)
        away_menu.pack(fill="x", padx=12, pady=(0, 12))

        inputs_box = ctk.CTkFrame(form, fg_color="#0f1b2e", corner_radius=10)
        inputs_box.pack(fill="x", pady=6)

        self.entries = {}

        def add_number_input(key, label):
            ctk.CTkLabel(inputs_box, text=label, text_color="gray").pack(anchor="w", padx=12, pady=(8, 2))
            entry = ctk.CTkEntry(inputs_box, fg_color="white", text_color=state.PRIMARY_BG)
            entry.pack(fill="x", padx=12, pady=(0, 4))
            self.entries[key] = entry

        add_number_input("h_fifa", "Home FIFA Rating")
        add_number_input("a_fifa", "Away FIFA Rating")
        add_number_input("h_form", "Home Form Last 5 Matches")
        add_number_input("a_form", "Away Form Last 5 Matches")
        add_number_input("h_goals_avg", "Home Goals Avg Last 5 Matches")
        add_number_input("a_goals_avg", "Away Goals Avg Last 5 Matches")

        result_box = ctk.CTkFrame(form, fg_color="#1E293B", corner_radius=10)
        result_box.pack(fill="x", pady=10)

        self.score_label = ctk.CTkLabel(result_box, text="Enter features and predict", font=("Arial", 16, "bold"), text_color=state.TEXT_COLOR)
        self.score_label.pack(pady=(12, 6))

        self.probs_label = ctk.CTkLabel(result_box, text="", font=("Arial", 12, "bold"), text_color="gray", justify="center")
        self.probs_label.pack(pady=(0, 12))

        self.matrix_container = ctk.CTkFrame(result_box, fg_color="transparent")
        self.matrix_container.pack(pady=(0, 12), padx=10)

        self.error_label = ctk.CTkLabel(form, text="", text_color="red")
        self.error_label.pack(pady=(0, 8))

        ctk.CTkButton(
            form,
            text="Predict Result",
            fg_color=state.ACCENT,
            height=40,
            command=self.predict_action
        ).pack(fill="x", pady=(0, 12))

    def read_float(self, key):
        value = self.entries[key].get().strip()
        if not value:
            raise ValueError("All fields are required.")
        return float(value)

    def get_color_for_prob(self, prob):
        if prob < 0.02:
            return "#dcfce7", "black"
        elif prob < 0.05:
            return "#bbf7d0", "black"
        elif prob < 0.08:
            return "#86efac", "black"
        elif prob < 0.12:
            return "#4ade80", "black"
        else:
            return "#16a34a", "white"

    def render_heatmap(self, matrix, home_name, away_name):
        for widget in self.matrix_container.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.matrix_container, text="", width=40).grid(row=0, column=0)
        for i in range(5):
            ctk.CTkLabel(self.matrix_container, text=str(i), font=("Arial", 12, "bold"), text_color="white", width=45).grid(row=0, column=i+1, pady=5)
        
        for h in range(5):
            ctk.CTkLabel(self.matrix_container, text=str(h), font=("Arial", 12, "bold"), text_color="white", width=40).grid(row=h+1, column=0, padx=5)
            for a in range(5):
                prob = matrix[h][a]
                bg_color, text_color = self.get_color_for_prob(prob)
                
                cell = ctk.CTkFrame(self.matrix_container, fg_color=bg_color, corner_radius=4, width=45, height=28)
                cell.grid(row=h+1, column=a+1, padx=2, pady=2)
                cell.pack_propagate(False)
                
                ctk.CTkLabel(cell, text=f"{prob*100:.1f}%", font=("Arial", 10, "bold"), text_color=text_color).pack(expand=True)
                
        legend = ctk.CTkLabel(self.matrix_container, text=f"Rows: {home_name} Goals  |  Cols: {away_name} Goals", font=("Arial", 11), text_color="gray")
        legend.grid(row=6, column=0, columnspan=6, pady=(10, 0))

    def predict_action(self):
        home = self.home_team_var.get()
        away = self.away_team_var.get()

        if home == away:
            self.error_label.configure(text="Choose two different teams.")
            return

        try:
            h_fifa_val = self.read_float("h_fifa")
            a_fifa_val = self.read_float("a_fifa")
            h_form_val = self.read_float("h_form")
            a_form_val = self.read_float("a_form")
            h_goals_avg_val = self.read_float("h_goals_avg")
            a_goals_avg_val = self.read_float("a_goals_avg")
        except ValueError:
            self.error_label.configure(text="Please enter valid numbers in all feature fields.")
            return

        if not (0 <= h_form_val <= 3.0) or not (0 <= a_form_val <= 3.0):
            self.error_label.configure(text="Form average must be between 0 and 3.")
            return

        self.error_label.configure(text="Predicting... Please wait.", text_color="gray")

        def background_task():
            try:
                predictor = utils.get_model_prediction()
                h_goals, a_goals, home_prob, draw_prob, away_prob = predictor(
                    home, away,
                    h_fifa_val, a_fifa_val,
                    h_form_val, a_form_val,
                    h_goals_avg_val, a_goals_avg_val
                )
                from Module import get_prediction_matrix
                prob_matrix = get_prediction_matrix(
                    home, away,
                    h_fifa_val, a_fifa_val,
                    h_form_val, a_form_val,
                    h_goals_avg_val, a_goals_avg_val,
                    max_goals=4
                )
                def on_success():
                    self.error_label.configure(text="")
                    self.score_label.configure(text=f"{home} {h_goals} - {a_goals} {away}", text_color=state.ACCENT)
                    self.probs_label.configure(
                        text=(
                            f"{home} Win: {home_prob * 100:.1f}%\n"
                            f"Draw: {draw_prob * 100:.1f}%\n"
                            f"{away} Win: {away_prob * 100:.1f}%"
                        ),
                        text_color="#facc15"
                    )
                    self.render_heatmap(prob_matrix, home, away)
                self.after(0, on_success)
            except Exception as e:
                def on_err():
                    self.error_label.configure(text=f"Prediction error: {e}", text_color="red")
                self.after(0, on_err)

        threading.Thread(target=background_task, daemon=True).start()
