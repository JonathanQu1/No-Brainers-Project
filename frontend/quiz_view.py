import customtkinter as ctk
from tkinter import messagebox

from frontend.quiz import load_questions
from frontend.user_store import get_attempt_count, get_last_score, save_score

SIDEBAR = "#1E293B"
MAIN_BG = "#F8FAFC"
CARD = "#FFFFFF"
PRIMARY = "#2563EB"
TEXT_DARK = "#0F172A"


class QuizView(ctk.CTkFrame):
    """Post-login area: sidebar, dashboard, profile, and true/false quiz (CSV scores)."""

    def __init__(self, parent, on_logout=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_logout = on_logout
        self._user = None
        self.current_user = ""
        self.questions = []
        self.current_index = 0
        self.score = 0

        self.configure(fg_color="transparent")

        self.body = ctk.CTkFrame(self, fg_color=MAIN_BG)
        self.body.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(self.body, fg_color=SIDEBAR, width=210, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="No Brainers",
            text_color="white",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(pady=(35, 35))

        ctk.CTkButton(
            sidebar,
            text="Dashboard",
            width=165,
            height=40,
            command=self._show_dashboard_page,
        ).pack(pady=8)

        ctk.CTkButton(
            sidebar,
            text="Start Quiz",
            width=165,
            height=40,
            command=self._start_quiz,
        ).pack(pady=8)

        ctk.CTkButton(
            sidebar,
            text="Profile",
            width=165,
            height=40,
            command=self._show_profile_page,
        ).pack(pady=8)

        ctk.CTkButton(
            sidebar,
            text="Logout",
            width=165,
            height=40,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._on_logout_click,
        ).pack(side="bottom", pady=30)

        self.main = ctk.CTkFrame(self.body, fg_color=MAIN_BG)
        self.main.pack(side="left", fill="both", expand=True, padx=35, pady=35)

    def set_user(self, user):
        self._user = user
        self.current_user = (getattr(user, "username", None) or "").strip() or "?"
        self._show_dashboard_page()

    def _clear_main_content(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def _show_dashboard_page(self):
        self._clear_main_content()

        ctk.CTkLabel(
            self.main,
            text=f"Welcome, {self.current_user}",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.main,
            text="Ready to test your knowledge today?",
            text_color="#64748B",
            font=ctk.CTkFont(size=16),
        ).pack(anchor="w", pady=(6, 28))

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

        ctk.CTkLabel(
            quiz_card,
            text="True / False Quiz Game",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(28, 8))

        ctk.CTkLabel(
            quiz_card,
            text="Answer simple True/False questions and track your score.",
            text_color="#64748B",
            font=ctk.CTkFont(size=15),
        ).pack(anchor="w", padx=30, pady=(0, 22))

        ctk.CTkButton(
            quiz_card,
            text="Start Quiz",
            width=220,
            height=45,
            fg_color=PRIMARY,
            command=self._start_quiz,
        ).pack(anchor="w", padx=30, pady=(0, 30))

    def _stat_card(self, parent, title, value, icon):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, width=190, height=110)
        card.pack(side="left", padx=(0, 18))
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24)).pack(
            anchor="w", padx=18, pady=(12, 0)
        )
        ctk.CTkLabel(
            card, text=title, text_color="#64748B", font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=18)
        ctk.CTkLabel(
            card,
            text=value,
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(2, 0))

    def _show_profile_page(self):
        self._clear_main_content()

        last_score = get_last_score(self.current_user)
        attempts = get_attempt_count(self.current_user)

        if last_score:
            score_text = f"{last_score['score']}/{last_score['total']}"
        else:
            score_text = "No attempts"

        ctk.CTkLabel(
            self.main,
            text="Profile",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w", pady=(0, 25))

        profile_card = ctk.CTkFrame(self.main, fg_color=CARD, corner_radius=18)
        profile_card.pack(anchor="w", fill="x", pady=10)

        ctk.CTkLabel(
            profile_card,
            text="User Information",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(28, 15))

        ctk.CTkLabel(
            profile_card,
            text=f"Username: {self.current_user}",
            font=ctk.CTkFont(size=17),
        ).pack(anchor="w", padx=30, pady=8)

        ctk.CTkLabel(
            profile_card,
            text=f"Total Attempts: {attempts}",
            font=ctk.CTkFont(size=17),
        ).pack(anchor="w", padx=30, pady=8)

        ctk.CTkLabel(
            profile_card,
            text=f"Last Quiz Score: {score_text}",
            font=ctk.CTkFont(size=17),
        ).pack(anchor="w", padx=30, pady=8)

        ctk.CTkButton(
            profile_card,
            text="Back to Dashboard",
            width=220,
            height=42,
            command=self._show_dashboard_page,
        ).pack(anchor="w", padx=30, pady=(20, 30))

    def _start_quiz(self):
        try:
            self.questions = load_questions()
        except (OSError, FileNotFoundError) as e:
            messagebox.showerror(
                "Error",
                "Could not load questions. Add data/questions.csv under the project root.",
            )
            return
        except KeyError:
            messagebox.showerror("Error", "questions.csv is missing required columns.")
            return

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
                f"Your final score is {self.score}/{len(self.questions)}",
            )

            self._show_dashboard_page()
            return

        q = self.questions[self.current_index]

        root = self.winfo_toplevel()
        quiz_window = ctk.CTkToplevel(root)
        quiz_window.title("True / False Quiz")
        quiz_window.geometry("560x360")
        quiz_window.grab_set()

        progress_value = (self.current_index + 1) / len(self.questions)

        ctk.CTkLabel(
            quiz_window,
            text=f"Question {self.current_index + 1} of {len(self.questions)}",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(pady=(28, 10))

        progress = ctk.CTkProgressBar(quiz_window, width=420)
        progress.pack(pady=(0, 25))
        progress.set(progress_value)

        ctk.CTkLabel(
            quiz_window,
            text=q["question"],
            font=ctk.CTkFont(size=20, weight="bold"),
            wraplength=460,
        ).pack(pady=20)

        row = ctk.CTkFrame(quiz_window, fg_color="transparent")
        row.pack(pady=25)

        ctk.CTkButton(
            row,
            text="True",
            width=150,
            height=45,
            fg_color="#16A34A",
            hover_color="#15803D",
            command=lambda: self._check_answer(True, quiz_window),
        ).pack(side="left", padx=18)

        ctk.CTkButton(
            row,
            text="False",
            width=150,
            height=45,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda: self._check_answer(False, quiz_window),
        ).pack(side="left", padx=18)

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

    def _on_logout_click(self):
        if self.on_logout is not None:
            self.on_logout()
