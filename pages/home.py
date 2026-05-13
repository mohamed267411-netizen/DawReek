import customtkinter as ctk
import state
import utils

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        ctk.CTkLabel(
            self,
            text="Season Analysis",
            font=("Arial", 20, "bold"),
            text_color=state.ACCENT
        ).pack(pady=(2, 6))

        self.images_by_season = utils.get_analysis_images()

        if not self.images_by_season:
            ctk.CTkLabel(
                self,
                text="No analysis images found.",
                text_color="gray",
                font=("Arial", 14)
            ).pack(expand=True)
            return

        self.seasons = sorted(self.images_by_season.keys(), reverse=True)
        self.season_var = ctk.StringVar(value=self.seasons[0])
        self.current_index = {"value": 0}

        controls = ctk.CTkFrame(self, fg_color="#0f1b2e", corner_radius=10)
        controls.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(controls, text="Season", text_color="gray").pack(anchor="w", padx=12, pady=(6, 2))
        season_menu = ctk.CTkOptionMenu(
            controls,
            values=self.seasons,
            variable=self.season_var,
            fg_color="#1E293B",
            button_color=state.ACCENT,
            command=self.change_season
        )
        season_menu.pack(fill="x", padx=12, pady=(0, 8))

        image_box = ctk.CTkFrame(self, fg_color="#0f1b2e", corner_radius=10, height=360)
        image_box.pack(fill="x", expand=False, pady=6)
        image_box.pack_propagate(False)
        image_box.grid_columnconfigure(0, weight=0)
        image_box.grid_columnconfigure(1, weight=1)
        image_box.grid_columnconfigure(2, weight=0)
        image_box.grid_rowconfigure(0, weight=1)

        self.image_label = ctk.CTkLabel(image_box, text="", height=430)
        self.image_label.grid(row=0, column=1, sticky="nsew", padx=6, pady=8)

        self.counter_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.counter_label.pack(pady=(2, 4))

        ctk.CTkButton(
            image_box,
            text="<",
            width=38,
            height=54,
            fg_color="#1E293B",
            command=self.previous_image
        ).grid(row=0, column=0, sticky="ns", padx=(8, 2), pady=8)

        ctk.CTkButton(
            image_box,
            text=">",
            width=38,
            height=54,
            fg_color=state.ACCENT,
            command=self.next_image
        ).grid(row=0, column=2, sticky="ns", padx=(2, 8), pady=8)

        self.render_image()

    def render_image(self):
        season_images = self.images_by_season.get(self.season_var.get(), [])
        if not season_images:
            self.image_label.configure(image=None, text="No images for this season.", text_color="gray")
            self.counter_label.configure(text="")
            return

        self.current_index["value"] %= len(season_images)
        image_path = season_images[self.current_index["value"]]
        img = utils.load_analysis_image(image_path)

        if img:
            self.image_label.configure(image=img, text="", height=430)
        else:
            self.image_label.configure(image=None, text="Could not load image.", text_color="red")

        self.counter_label.configure(text=f"{self.current_index['value'] + 1} / {len(season_images)}")

    def change_season(self, *args):
        self.current_index["value"] = 0
        self.render_image()

    def previous_image(self):
        self.current_index["value"] -= 1
        self.render_image()

    def next_image(self):
        self.current_index["value"] += 1
        self.render_image()
