import customtkinter as ctk
from tkinter import messagebox

from backend.auth_service import login, signup


class LoginView(ctk.CTkFrame):
    def __init__(self, parent, on_success=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_success = on_success
        self.configure(fg_color="transparent")

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)

        for i in (0, 2):
            outer.grid_rowconfigure(i, weight=1)
            outer.grid_columnconfigure(i, weight=1)

        center = ctk.CTkFrame(outer, fg_color="transparent")
        center.grid(row=1, column=1)

        self._login = ctk.CTkFrame(center, fg_color="transparent")
        self._build_login(self._login)
        self._login.pack(fill="both", expand=True)

        self._signup = ctk.CTkFrame(center, fg_color="transparent")
        self._build_signup(self._signup)

    def _build_login(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack()

        ctk.CTkLabel(
            card,
            text="Welcome to the login page",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 16), padx=32)

        ctk.CTkLabel(card, text="Username").pack(anchor="center")
        self.login_username = ctk.CTkEntry(
            card, placeholder_text="Username", width=240
        )
        self.login_username.pack(pady=(4, 12), padx=32)

        ctk.CTkLabel(card, text="Password").pack(anchor="center")
        self.login_password = ctk.CTkEntry(
            card, placeholder_text="Password", show="*", width=240
        )
        self.login_password.pack(pady=(4, 20), padx=32)

        ctk.CTkButton(card, text="Log in", width=240, command=self._on_login).pack(
            pady=(0, 20)
        )

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(8, 0))
        ctk.CTkLabel(row, text="Don't have an account? ").pack(side="left")
        link = ctk.CTkLabel(
            row,
            text="Sign up",
            text_color=("#1f6aa5", "#5b9ee2"),
            cursor="hand2",
            font=ctk.CTkFont(size=13, underline=True),
        )
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._show_signup())

    def _build_signup(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack()

        ctk.CTkLabel(
            card,
            text="Sign up",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 16), padx=32)

        ctk.CTkLabel(card, text="Username").pack(anchor="center")
        self.signup_username = ctk.CTkEntry(
            card, placeholder_text="Username", width=240
        )
        self.signup_username.pack(pady=(4, 12), padx=32)

        ctk.CTkLabel(card, text="Password").pack(anchor="center")
        self.signup_password = ctk.CTkEntry(
            card, placeholder_text="Password", width=240, show="*"
        )
        self.signup_password.pack(pady=(4, 20), padx=32)

        ctk.CTkLabel(card, text="Confirm Password").pack(anchor="center")
        self.signup_confirm = ctk.CTkEntry(
            card, placeholder_text="Confirm Password", width=240, show="*"
        )
        self.signup_confirm.pack(pady=(4, 20), padx=32)

        ctk.CTkButton(card, text="Submit", width=240, command=self._on_submit).pack(
            pady=(0, 20)
        )

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(0, 20))
        ctk.CTkLabel(row, text="Already have an account? ").pack(side="left")
        back = ctk.CTkLabel(
            row,
            text="Log in",
            text_color=("#1f6aa5", "#5b9ee2"),
            cursor="hand2",
            font=ctk.CTkFont(size=13, underline=True),
        )
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self._show_login())

    def _show_signup(self):
        self._login.pack_forget()
        self._signup.pack(fill="both", expand=True)

    def _show_login(self):
        self._signup.pack_forget()
        self._login.pack(fill="both", expand=True)

    def _on_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        ok, msg, user = login(username, password)
        if ok:
            messagebox.showinfo("Login", msg)
            if self.on_success is not None:
                self.on_success(user)
        else:
            messagebox.showerror("Login", msg)

    def _on_submit(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm = self.signup_confirm.get()

        if password != confirm:
            messagebox.showerror("Sign up", "Passwords do not match")
            return
        ok, msg = signup(username, password)

        if ok:
            messagebox.showinfo("Sign up", msg)
            self._show_login()
        else:
            messagebox.showerror("Sign up", msg)
