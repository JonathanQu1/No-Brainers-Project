import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image

from backend.auth_service import login, signup


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_success=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_success = on_success
        self.configure(fg_color="transparent")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True)

        self.login_card = None
        self.signup_card = None

        self._build_login()
        self._build_signup()

        self.show_login()

    # login page
    def _build_login(self):
        self.login_card = ctk.CTkFrame(
            self.container,
            corner_radius=12,
            width=360,
            height=460,
        )
        self.login_card.pack_propagate(False)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(BASE_DIR, "logo.png")

        self.logo_image = ctk.CTkImage(
            light_image=Image.open(logo_path),
            dark_image=Image.open(logo_path),
            size=(90, 90),
        )

        ctk.CTkLabel(
            self.login_card,
            image=self.logo_image,
            text="No-Brainers",
            compound="bottom",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(25, 15))

        ctk.CTkLabel(self.login_card, text="Username").pack()
        self.login_username = ctk.CTkEntry(self.login_card, width=240)
        self.login_username.pack(pady=5)

        ctk.CTkLabel(self.login_card, text="Password").pack()
        self.login_password = ctk.CTkEntry(self.login_card, show="*", width=240)
        self.login_password.pack(pady=5)

        ctk.CTkButton(
            self.login_card,
            text="Log In",
            width=240,
            command=self._on_login,
        ).pack(pady=(15, 10))

        link = ctk.CTkLabel(
            self.login_card,
            text="Sign Up",
            text_color="#1f6aa5",
            cursor="hand2",
            font=ctk.CTkFont(underline=True),
        )
        link.pack()
        link.bind("<Button-1>", lambda e: self.show_signup())

    # signup page
    def _build_signup(self):
        self.signup_card = ctk.CTkFrame(
            self.container,
            corner_radius=12,
            width=360,
            height=460,
        )
        self.signup_card.pack_propagate(False)

        ctk.CTkLabel(
            self.signup_card,
            text="Sign up",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(25, 15))

        ctk.CTkLabel(self.signup_card, text="Enter Username").pack()
        self.signup_username = ctk.CTkEntry(self.signup_card, width=240)
        self.signup_username.pack(pady=(4, 10))

        ctk.CTkLabel(self.signup_card, text="Enter Password").pack()
        self.signup_password = ctk.CTkEntry(self.signup_card, show="*", width=240)
        self.signup_password.pack(pady=(4, 10))

        ctk.CTkLabel(self.signup_card, text="Confirm Password").pack()
        self.signup_confirm = ctk.CTkEntry(self.signup_card, show="*", width=240)
        self.signup_confirm.pack(pady=(4, 15))

        ctk.CTkButton(
            self.signup_card,
            text="Create Account",
            width=240,
            command=self._on_submit,
        ).pack(pady=15)

        back = ctk.CTkLabel(
            self.signup_card,
            text="Back to Login",
            text_color="#1f6aa5",
            cursor="hand2",
            font=ctk.CTkFont(underline=True),
        )
        back.pack()
        back.bind("<Button-1>", lambda e: self.show_login())

    def show_login(self):
        self.signup_card.pack_forget()
        self.login_card.pack(expand=True, anchor="n", pady=80)

    def show_signup(self):
        self.login_card.pack_forget()
        self.signup_card.pack(expand=True, anchor="n", pady=80)

    def _on_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()

        ok, msg, user = login(username, password)

        if ok:
            messagebox.showinfo("Login", msg)
            if self.on_success:
                self.on_success(user)
        else:
            messagebox.showerror("Login", msg)

    def _on_submit(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm = self.signup_confirm.get()

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        ok, msg = signup(username, password)

        if ok:
            messagebox.showinfo("Success", msg)
            self.show_login()
        else:
            messagebox.showerror("Error", msg)
