import customtkinter as ctk
import state
import utils

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        self.pack_propagate(False)

        container = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        container.pack(fill="both", expand=True, padx=20, pady=45)

        self.draw_app_name_in_login(container)

        login_img = utils.load_image_safe(state.LOGIN_IMG_PATH, size=(270, 120), rounded=False)
        if login_img:
            ctk.CTkLabel(container, image=login_img, text="", corner_radius=50).pack(pady=(0, 12))

        frame = ctk.CTkFrame(container, fg_color=state.PRIMARY_BG)
        frame.pack(fill="both", expand=True)

        welcome_label = ctk.CTkLabel(frame, text="Welcome Back", font=("Arial", 18, "bold"), text_color=state.TEXT_COLOR)
        welcome_label.pack(pady=(10, 6))

        subtitle = ctk.CTkLabel(frame, text="Login to continue", font=("Arial", 12), text_color="lightgray")
        subtitle.pack(pady=(0, 12))

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.email_entry.pack(pady=10, fill="x")

        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.pass_entry.pack(pady=10, fill="x")

        forgot_btn = ctk.CTkButton(frame,
                                   text="Forgot Password?",
                                   fg_color="transparent",
                                   text_color=state.ACCENT,
                                   hover_color=None,
                                   border_width=0,
                                   command=lambda: self.controller.show_page("ForgotPasswordPage"))
        forgot_btn.pack(pady=(0,8), anchor="e")

        self.error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.error_label.pack()

        login_btn = ctk.CTkButton(frame, text="Log in", command=self.login_action, fg_color=state.ACCENT)
        login_btn.pack(pady=10, fill="x")

        signup_btn = ctk.CTkButton(frame, text="Sign up", fg_color="transparent", text_color=state.ACCENT, command=lambda: self.controller.show_page("SignupPage"), border_width=2)
        signup_btn.pack(pady=10, fill="x")

        skip_btn = ctk.CTkButton(frame, text="Continue as Guest", fg_color="transparent", text_color=state.ACCENT, border_width=2, command=self.continue_as_guest)
        skip_btn.pack(pady=10, fill="x")

    def draw_app_name_in_login(self, parent):
        header = ctk.CTkFrame(parent, fg_color=state.PRIMARY_BG, corner_radius=0)
        header.pack(fill="x", pady=(0,10))
        app_label = ctk.CTkLabel(header, text="DawReeK APP", font=("Arial", 20, "bold"), text_color=state.ACCENT)
        app_label.pack(pady=6)

    def login_action(self):
        email = self.email_entry.get().strip()
        raw_pass = self.pass_entry.get()
        if not email or not raw_pass:
            self.error_label.configure(text="Enter email and password")
            return
        password = utils.hash_password(raw_pass)
        
        if state.cursor:
            state.cursor.execute("SELECT * FROM Users WHERE Email=? AND PasswordHash=?", (email, password))
            user = state.cursor.fetchone()
            if user:
                state.current_user_email = email
                self.controller.show_page("HomePage")
            else:
                self.error_label.configure(text="Invalid credentials")
        else:
            self.error_label.configure(text="Database connection error")

    def continue_as_guest(self):
        state.is_guest = True
        state.current_user_email = None
        self.controller.show_page("HomePage")

class ForgotPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        container = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        container.pack(fill="both", expand=True, padx=20, pady=70)

        top_row = ctk.CTkFrame(container, fg_color=state.PRIMARY_BG)
        top_row.pack(fill="x")
        back_btn = ctk.CTkButton(top_row, text="⬅️ Back", fg_color="transparent", text_color=state.TEXT_COLOR,
                                 command=lambda: self.controller.show_page("LoginPage"), width=70)
        back_btn.pack(side="left")

        title = ctk.CTkLabel(container, text="Forgot Password", font=("Arial", 22, "bold"), text_color=state.TEXT_COLOR)
        title.pack(pady=(100,6))
        instr = ctk.CTkLabel(container, text="Please enter your email to reset the password.", font=("Arial", 12), text_color="lightgray")
        instr.pack(pady=(0,12))

        self.email_entry = ctk.CTkEntry(container, placeholder_text="Example@gmail.com", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.email_entry.pack(pady=10, fill="x")

        self.msg_label = ctk.CTkLabel(container, text="", text_color=state.TEXT_COLOR)
        self.msg_label.pack(pady=(6,0))

        reset_btn = ctk.CTkButton(container, text="Reset Password", command=self.reset_action, fg_color=state.ACCENT, width=200, height=50)
        reset_btn.pack(pady=10)

    def reset_action(self):
        email = self.email_entry.get().strip()
        if not email:
            self.msg_label.configure(text="Enter your email", text_color="red")
            return
        if state.cursor:
            state.cursor.execute("SELECT UserID FROM Users WHERE Email=?", (email,))
            row = state.cursor.fetchone()
            if not row:
                self.msg_label.configure(text="Email not found", text_color="red")
                return
            
            # Pass email to NewPasswordPage somehow. In this setup, we can set a controller variable or pass it to a method
            self.controller.get_page("NewPasswordPage").set_email(email)
            self.controller.show_page("NewPasswordPage")
        else:
            self.msg_label.configure(text="Database connection error", text_color="red")

class NewPasswordPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller
        self.email = ""

        frame = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        frame.pack(fill="both", expand=True, padx=20, pady=100)

        title = ctk.CTkLabel(frame, text="Set New Password", font=("Arial", 22, "bold"), text_color=state.TEXT_COLOR)
        title.pack(pady=(20, 8))

        self.instr = ctk.CTkLabel(frame, text="Resetting password for: ", font=("Arial", 11), text_color="lightgray")
        self.instr.pack(pady=(0, 12))

        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="New Password", show="*", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.pass_entry.pack(pady=10, fill="x")

        self.pass_confirm = ctk.CTkEntry(frame, placeholder_text="Confirm New Password", show="*", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.pass_confirm.pack(pady=10, fill="x")

        self.msg_label = ctk.CTkLabel(frame, text="", text_color=state.TEXT_COLOR)
        self.msg_label.pack(pady=(6,0))

        save_btn = ctk.CTkButton(frame, text="Save New Password", command=self.save_new_password, fg_color=state.ACCENT)
        save_btn.pack(pady=20, fill="x")

        cancel_btn = ctk.CTkButton(frame, text="Cancel", command=lambda: self.controller.show_page("LoginPage"), fg_color="transparent", text_color=state.ACCENT, border_width=1)
        cancel_btn.pack(pady=(0,8), fill="x")

    def set_email(self, email):
        self.email = email
        self.instr.configure(text=f"Resetting password for: {email}")

    def save_new_password(self):
        new_pass = self.pass_entry.get().strip()
        confirm = self.pass_confirm.get().strip()
        if not new_pass or not confirm:
            self.msg_label.configure(text="Enter and confirm the new password", text_color="red")
            return
        if new_pass != confirm:
            self.msg_label.configure(text="Passwords do not match", text_color="red")
            return
        try:
            if state.cursor:
                state.cursor.execute("UPDATE Users SET PasswordHash=? WHERE Email=?", (utils.hash_password(new_pass), self.email))
                state.conn.commit()
                self.controller.show_page("PasswordSuccessPage")
            else:
                self.msg_label.configure(text="Database connection error", text_color="red")
        except Exception:
            self.msg_label.configure(text="Error updating password", text_color="red")


class PasswordSuccessPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        frame = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        frame.pack(fill="both", expand=True, padx=20, pady=100)

        check_icon = utils.load_image_safe(state.CHECK_ICON_PATH, size=(120, 120))
        if check_icon:
            icon_label = ctk.CTkLabel(frame, image=check_icon, text="")
            icon_label.pack(pady=(100, 10))
        else:
            icon_label = ctk.CTkLabel(frame, text="✔️", font=("Arial", 48, "bold"), text_color=state.ACCENT)
            icon_label.pack(padx=10,pady=(100, 10))

        title = ctk.CTkLabel(frame, text="You're all set!", font=("Arial", 20, "bold"), text_color=state.TEXT_COLOR)
        title.pack(pady=(6,4))

        subtitle = ctk.CTkLabel(frame, text="Congratulations! Your password has been changed.", font=("Arial", 12), text_color="lightgray")
        subtitle.pack(pady=(0,8))

        instr = ctk.CTkLabel(frame, text="Click Continue to login", font=("Arial", 11), text_color="lightgray")
        instr.pack(pady=(0,12))

        continue_btn = ctk.CTkButton(frame, text="Continue", command=lambda: self.controller.show_page("LoginPage"), fg_color=state.ACCENT)
        continue_btn.pack(pady=20, fill="x")

class SignupPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=state.PRIMARY_BG)
        self.controller = controller

        container = ctk.CTkFrame(self, fg_color=state.PRIMARY_BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        frame = ctk.CTkFrame(container, fg_color=state.PRIMARY_BG)
        frame.pack(fill="both", expand=True)

        login_img = utils.load_image_safe(state.LOGIN_IMG_PATH, size=(270, 120), rounded=False)
        if login_img:
            ctk.CTkLabel(frame, image=login_img, text="", corner_radius=50).pack(pady=(50, 12))

        title = ctk.CTkLabel(frame, text="Sign Up", font=("Arial", 22, "bold"), text_color=state.TEXT_COLOR)
        title.pack(pady=20)

        self.name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.name_entry.pack(pady=10, fill="x")

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.email_entry.pack(pady=10, fill="x")

        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", fg_color=state.TEXT_COLOR, text_color=state.PRIMARY_BG)
        self.pass_entry.pack(pady=10, fill="x")

        self.msg_label = ctk.CTkLabel(frame, text="", text_color=state.TEXT_COLOR)
        self.msg_label.pack()

        signup_btn = ctk.CTkButton(frame, text="Sign up", command=self.signup_action, fg_color=state.ACCENT)
        signup_btn.pack(pady=20, fill="x")
        
        back_btn = ctk.CTkButton(frame, text="Back to Login", command=lambda: self.controller.show_page("LoginPage"), fg_color="transparent", text_color=state.ACCENT, border_width=1)
        back_btn.pack(pady=(0, 10), fill="x")

    def signup_action(self):
        fullname = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.pass_entry.get()
        if not fullname or not email or not password:
            self.msg_label.configure(text="Please Fill all fields", text_color="red")
            return
        try:
            if state.cursor:
                state.cursor.execute("INSERT INTO Users (FullName, Email, PasswordHash) VALUES (?, ?, ?)",
                                    (fullname, email, utils.hash_password(password)))
                state.conn.commit()
                state.current_user_email = email 
                self.controller.show_page("TeamSelectionPage")
            else:
                self.msg_label.configure(text="Database connection error", text_color="red")
        except Exception:
            self.msg_label.configure(text="Email already exists", text_color="red")
