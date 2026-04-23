import customtkinter as ctk


class QuizView(ctk.CTkFrame):
    def __init__(self, parent, on_logout=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_logout = on_logout
        self._user = None
        self.configure(fg_color="transparent")

        card = ctk.CTkFrame(self, corner_radius=12, fg_color="lightblue")
        card.pack(expand=True, pady=32, padx=32, fill="both")

        self._title = ctk.CTkLabel(
            card,
            text="Main",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self._title.pack(pady=(24, 8))

        self._user_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=14),
        )
        self._user_label.pack(pady=(0, 24))

        ctk.CTkButton(
            card,
            text="Log out",
            width=200,
            command=self._on_logout_click,
        ).pack(pady=(0, 24))

    def set_user(self, user):
        self._user = user
        name = getattr(user, "username", None) or "?"
        self._user_label.configure(text=f"Signed in as: {name}")

    def _on_logout_click(self):
        if self.on_logout is not None:
            self.on_logout()
