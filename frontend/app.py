import customtkinter as ctk
from tkinter import messagebox
from user_store import signup_user, verify_user, save_score, get_last_score, get_attempt_count

from frontend.login_view import LoginView
from frontend.quiz_view import QuizView

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

SIDEBAR = "#1E293B"
MAIN_BG = "#F8FAFC"
CARD = "#FFFFFF"
PRIMARY = "#2563EB"
TEXT_DARK = "#0F172A"


<<<<<<< Updated upstream
=======
class LoginForm:
    def __init__(self, root):
        self.root = root
        self.root.title("No Brainers Quiz App")
        self.root.geometry("950x620")

        self.current_user = ""
        self.questions = []
        self.current_index = 0
        self.score = 0

        self.container = ctk.CTkFrame(self.root, fg_color=MAIN_BG)
        self.container.pack(fill="both", expand=True)

        self._login = ctk.CTkFrame(self.container, fg_color=MAIN_BG)
        self._signup = ctk.CTkFrame(self.container, fg_color=MAIN_BG)
        self._dashboard = ctk.CTkFrame(self.container, fg_color=MAIN_BG)

        self._build_login()
        self._build_signup()
        self._build_dashboard()
        self._show_login()

    def _clear_pages(self):
        self._login.pack_forget()
        self._signup.pack_forget()
        self._dashboard.pack_forget()

    def _center_page(self, page):
        self._clear_pages()
        page.pack(fill="both", expand=True)

    def _build_login(self):
        card = ctk.CTkFrame(self._login, fg_color=CARD, corner_radius=18)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="No Brainers",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(30, 5), padx=50)

        ctk.CTkLabel(card, text="Login to start your quiz",
                     font=ctk.CTkFont(size=15),
                     text_color="#64748B").pack(pady=(0, 25))

        ctk.CTkLabel(card, text="Username").pack(anchor="w", padx=45)
        self.login_username = ctk.CTkEntry(card, width=300, height=38)
        self.login_username.pack(pady=(6, 15), padx=45)

        ctk.CTkLabel(card, text="Password").pack(anchor="w", padx=45)
        self.login_password = ctk.CTkEntry(card, width=300, height=38, show="*")
        self.login_password.pack(pady=(6, 22), padx=45)

        ctk.CTkButton(card, text="Log in", width=300, height=42,
                      fg_color=PRIMARY, command=self._on_login).pack(pady=(0, 20))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(0, 30))

        ctk.CTkLabel(row, text="Don't have an account? ").pack(side="left")
        link = ctk.CTkLabel(row, text="Sign up", text_color=PRIMARY,
                            cursor="hand2", font=ctk.CTkFont(underline=True))
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._show_signup())

    def _build_signup(self):
        card = ctk.CTkFrame(self._signup, fg_color=CARD, corner_radius=18)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="Create Account",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(30, 20), padx=50)

        ctk.CTkLabel(card, text="Username").pack(anchor="w", padx=45)
        self.signup_username = ctk.CTkEntry(card, width=300, height=38)
        self.signup_username.pack(pady=(6, 14), padx=45)

        ctk.CTkLabel(card, text="Password").pack(anchor="w", padx=45)
        self.signup_password = ctk.CTkEntry(card, width=300, height=38, show="*")
        self.signup_password.pack(pady=(6, 14), padx=45)

        ctk.CTkLabel(card, text="Confirm Password").pack(anchor="w", padx=45)
        self.confirm_password = ctk.CTkEntry(card, width=300, height=38, show="*")
        self.confirm_password.pack(pady=(6, 22), padx=45)

        ctk.CTkButton(card, text="Create Account", width=300, height=42,
                      fg_color=PRIMARY, command=self._on_submit).pack(pady=(0, 20))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(0, 30))

        ctk.CTkLabel(row, text="Already have an account? ").pack(side="left")
        link = ctk.CTkLabel(row, text="Log in", text_color=PRIMARY,
                            cursor="hand2", font=ctk.CTkFont(underline=True))
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._show_login())

    def _build_dashboard(self):
        sidebar = ctk.CTkFrame(self._dashboard, fg_color=SIDEBAR, width=210, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="No Brainers",
                     text_color="white",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(35, 35))

        ctk.CTkButton(sidebar, text="Dashboard", width=165, height=40,
                      command=self._show_dashboard_page).pack(pady=8)

        ctk.CTkButton(sidebar, text="Start Quiz", width=165, height=40,
                      command=self._start_quiz).pack(pady=8)

        ctk.CTkButton(sidebar, text="Profile", width=165, height=40,
                      command=self._show_profile_page).pack(pady=8)

        ctk.CTkButton(sidebar, text="Logout", width=165, height=40,
                      fg_color="#EF4444", hover_color="#DC2626",
                      command=self._show_login).pack(side="bottom", pady=30)

        self.main = ctk.CTkFrame(self._dashboard, fg_color=MAIN_BG)
        self.main.pack(side="left", fill="both", expand=True, padx=35, pady=35)

    def _clear_main_content(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def _show_dashboard_page(self):
        self._clear_main_content()

        ctk.CTkLabel(self.main, text=f"Welcome, {self.current_user}",
                     text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=30, weight="bold")).pack(anchor="w")

        ctk.CTkLabel(self.main, text="Ready to test your knowledge today?",
                     text_color="#64748B",
                     font=ctk.CTkFont(size=16)).pack(anchor="w", pady=(6, 28))

        stats = ctk.CTkFrame(self.main, fg_color="transparent")
        stats.pack(anchor="w", fill="x", pady=(0, 25))

        last_score = get_last_score(self.current_user)
        attempts = get_attempt_count(self.current_user)

        if last_score:
            score_text = f"{last_score['score']}/{last_score['total']}"
            accuracy = f"{round((int(last_score['score']) / int(last_score['total'])) * 100)}%"
        else:
            score_text = "No attempts"
            accuracy = "0%"

        self._stat_card(stats, "Attempts", str(attempts), "📚")
        self._stat_card(stats, "Last Score", score_text, "⭐")
        self._stat_card(stats, "Accuracy", accuracy, "🎯")

        quiz_card = ctk.CTkFrame(self.main, fg_color=CARD, corner_radius=18)
        quiz_card.pack(anchor="w", fill="x", pady=10)

        ctk.CTkLabel(quiz_card, text="True / False Quiz Game",
                     text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=30, pady=(28, 8))

        ctk.CTkLabel(quiz_card,
                     text="Answer simple True/False questions and track your score.",
                     text_color="#64748B",
                     font=ctk.CTkFont(size=15)).pack(anchor="w", padx=30, pady=(0, 22))

        ctk.CTkButton(quiz_card, text="Start Quiz", width=220, height=45,
                      fg_color=PRIMARY, command=self._start_quiz).pack(anchor="w", padx=30, pady=(0, 30))

    def _stat_card(self, parent, title, value, icon):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, width=190, height=110)
        card.pack(side="left", padx=(0, 18))
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24)).pack(anchor="w", padx=18, pady=(12, 0))
        ctk.CTkLabel(card, text=title, text_color="#64748B",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=18)
        ctk.CTkLabel(card, text=value, text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=18, pady=(2, 0))

    def _show_profile_page(self):
        self._clear_main_content()

        last_score = get_last_score(self.current_user)
        attempts = get_attempt_count(self.current_user)

        if last_score:
            score_text = f"{last_score['score']}/{last_score['total']}"
        else:
            score_text = "No attempts"

        ctk.CTkLabel(self.main, text="Profile",
                     text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=30, weight="bold")).pack(anchor="w", pady=(0, 25))

        profile_card = ctk.CTkFrame(self.main, fg_color=CARD, corner_radius=18)
        profile_card.pack(anchor="w", fill="x", pady=10)

        ctk.CTkLabel(profile_card, text="User Information",
                     text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=30, pady=(28, 15))

        ctk.CTkLabel(profile_card, text=f"Username: {self.current_user}",
                     font=ctk.CTkFont(size=17)).pack(anchor="w", padx=30, pady=8)

        ctk.CTkLabel(profile_card, text=f"Total Attempts: {attempts}",
                     font=ctk.CTkFont(size=17)).pack(anchor="w", padx=30, pady=8)

        ctk.CTkLabel(profile_card, text=f"Last Quiz Score: {score_text}",
                     font=ctk.CTkFont(size=17)).pack(anchor="w", padx=30, pady=8)

        ctk.CTkButton(profile_card, text="Back to Dashboard", width=220, height=42,
                      command=self._show_dashboard_page).pack(anchor="w", padx=30, pady=(20, 30))

    def _show_login(self):
        self.current_user = ""
        self.login_username.delete(0, "end")
        self.login_password.delete(0, "end")
        self._center_page(self._login)

    def _show_signup(self):
        self._center_page(self._signup)

    def _show_dashboard(self, username):
        self.current_user = username
        self._center_page(self._dashboard)
        self._show_dashboard_page()

    def _on_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please enter username and password.")
            return

        if not verify_user(username, password):
            messagebox.showerror("Login Failed", "User not found or password is incorrect.")
            return

        self._show_dashboard(username)

    def _on_submit(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm = self.confirm_password.get().strip()

        if username == "" or password == "" or confirm == "":
            messagebox.showerror("Error", "Please fill all fields.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        created = signup_user(username, password)

        if not created:
            messagebox.showerror("Error", "Username already exists. Please log in.")
            return

        messagebox.showinfo("Signup Success", "Account created successfully. Please log in.")
        self.signup_username.delete(0, "end")
        self.signup_password.delete(0, "end")
        self.confirm_password.delete(0, "end")
        self._show_login()

    def _start_quiz(self):
        from quiz import load_questions

        self.questions = load_questions()
        self.current_index = 0
        self.score = 0

        if len(self.questions) == 0:
            messagebox.showerror("Error", "No questions found.")
            return

        self._show_question()

    def _show_question(self):
        if self.current_index >= len(self.questions):
            save_score(self.current_user, self.score, len(self.questions))

            messagebox.showinfo(
                "Quiz Finished",
                f"Your final score is {self.score}/{len(self.questions)}"
            )

            self._show_dashboard_page()
            return

        q = self.questions[self.current_index]

        quiz_window = ctk.CTkToplevel(self.root)
        quiz_window.title("True / False Quiz")
        quiz_window.geometry("560x360")
        quiz_window.grab_set()

        progress_value = (self.current_index + 1) / len(self.questions)

        ctk.CTkLabel(
            quiz_window,
            text=f"Question {self.current_index + 1} of {len(self.questions)}",
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(28, 10))

        progress = ctk.CTkProgressBar(quiz_window, width=420)
        progress.pack(pady=(0, 25))
        progress.set(progress_value)

        ctk.CTkLabel(
            quiz_window,
            text=q["question"],
            font=ctk.CTkFont(size=20, weight="bold"),
            wraplength=460
        ).pack(pady=20)

        row = ctk.CTkFrame(quiz_window, fg_color="transparent")
        row.pack(pady=25)

        ctk.CTkButton(row, text="True", width=150, height=45,
                      fg_color="#16A34A", hover_color="#15803D",
                      command=lambda: self._check_answer(True, quiz_window)).pack(side="left", padx=18)

        ctk.CTkButton(row, text="False", width=150, height=45,
                      fg_color="#DC2626", hover_color="#B91C1C",
                      command=lambda: self._check_answer(False, quiz_window)).pack(side="left", padx=18)

    def _check_answer(self, user_answer, window):
        correct_answer = self.questions[self.current_index]["answer"]

        if user_answer == correct_answer:
            self.score += 1
            messagebox.showinfo("Correct", "Correct answer!")
        else:
            messagebox.showerror("Wrong", "Wrong answer!")

        window.destroy()
        self.current_index += 1
        self._show_question()


>>>>>>> Stashed changes
def main():
    root = ctk.CTk()
    root.title("No Brainers")
    root.geometry("900x600")

    container = ctk.CTkFrame(root, fg_color="transparent")
    container.pack(fill="both", expand=True)

    def show_quiz(user):
        login_view.pack_forget()
        quiz_view.set_user(user)
        quiz_view.pack(fill="both", expand=True)

    def show_login():
        quiz_view.pack_forget()
        login_view.pack(fill="both", expand=True)

    login_view = LoginView(container, on_success=show_quiz, fg_color="transparent")
    quiz_view = QuizView(container, on_logout=show_login, fg_color="transparent")

    login_view.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()