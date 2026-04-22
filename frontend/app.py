import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


class LoginForm:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Login Page")
        self.root.geometry("900x600")

        outer = ctk.CTkFrame(self.root, fg_color="transparent")
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

    def _build_login(self, parent: ctk.CTkFrame):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack()

        ctk.CTkLabel(
            card,
            text="Welcome to the login page",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 16), padx=32)

        ctk.CTkLabel(card, text="Username").pack(anchor="center")
        self.username = ctk.CTkEntry(card, placeholder_text="Username", width=240)
        self.username.pack(pady=(4, 12), padx=32)

        ctk.CTkLabel(card, text="Password").pack(anchor="center")
        self.password = ctk.CTkEntry(
            card, placeholder_text="Password", show="*", width=240
        )
        self.password.pack(pady=(4, 20), padx=32)

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

    def _build_signup(self, parent: ctk.CTkFrame):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack()

        ctk.CTkLabel(
            card,
            text="Sign up",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 16), padx=32)

        ctk.CTkLabel(card, text="Username").pack(anchor="center")
        self.username = ctk.CTkEntry(card, placeholder_text="Username", width=240)
        self.username.pack(pady=(4, 12), padx=32)

        ctk.CTkLabel(card, text="Password").pack(anchor="center")
        self.password = ctk.CTkEntry(
            card, placeholder_text="Password", width=240
        )
        self.password.pack(pady=(4, 20), padx=32)

        ctk.CTkLabel(card, text="Confirm Password").pack(anchor="center")
        self.password = ctk.CTkEntry(
            card, placeholder_text="Confirm Password", width=240
        )
        self.password.pack(pady=(4, 20), padx=32)

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
        print(self.username.get(), self.password.get())

    def _on_submit(self):
        print("submit") 

def main():
    root = ctk.CTk()
    LoginForm(root)
    root.mainloop()


if __name__ == "__main__":
    main()