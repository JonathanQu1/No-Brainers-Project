import os

import customtkinter as ctk
from tkinter import filedialog, messagebox

from frontend.flashcard_view import FlashcardPanel
from frontend.quiz import load_questions, parse_questions_csv
from frontend.user_store import (
    get_attempt_count,
    get_last_score,
    get_user_stats,
    save_score,
)

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
            text="Create Flashcard",
            width=165,
            height=40,
            command=self._show_create_flashcard,
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
        ).pack(side="left", padx=30, pady=(0, 22))

        ctk.CTkButton(
            quiz_card,
            text="Import Quiz",
            width=220,
            height=45,
            fg_color=PRIMARY,
            command=self._import_quiz,
        ).pack(side="left", pady=(0, 22))

    def _get_rank(self, stats):
        """Return (name, color, icon) for the user's rank tier."""
        attempts = stats["attempts"]
        if attempts >= 30:
            return ("Master", "#7C3AED", "👑")
        if attempts >= 15:
            return ("Pro", "#EA580C", "🏆")
        if attempts >= 5:
            return ("Novice", "#2563EB", "🎓")
        return ("Beginner", "#16A34A", "🌱")

    def _get_achievements(self, stats):
        """Return list of (icon, title, description, unlocked) tuples."""
        return [
            (
                "🎯",
                "First Quiz",
                "Complete your first quiz",
                stats["attempts"] >= 1,
            ),
            (
                "🔥",
                "Quiz Master",
                "Complete 5 quizzes",
                stats["attempts"] >= 5,
            ),
            (
                "⭐",
                "Accuracy Expert",
                "Achieve 90%+ accuracy",
                stats["accuracy"] >= 90 and stats["attempts"] >= 1,
            ),
        ]

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

    def _info_card(self, parent, title, value, icon, value_color):
        card = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16, width=290, height=100)
        card.pack(side="left", padx=(0, 18))
        card.pack_propagate(False)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(anchor="w", fill="x", padx=18, pady=(14, 0))

        ctk.CTkLabel(
            header, text=icon, font=ctk.CTkFont(size=20)
        ).pack(side="left")
        ctk.CTkLabel(
            header,
            text=title,
            text_color="#64748B",
            font=ctk.CTkFont(size=13),
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            card,
            text=value,
            text_color=value_color,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w", padx=18, pady=(4, 0))

    def _achievement_card(self, parent, icon, title, desc, unlocked):
        bg = CARD if unlocked else "#F1F5F9"
        title_color = TEXT_DARK if unlocked else "#94A3B8"
        desc_color = "#475569" if unlocked else "#94A3B8"
        badge_text = "✓ Unlocked" if unlocked else "🔒 Locked"
        badge_color = "#16A34A" if unlocked else "#94A3B8"

        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=16, width=210, height=170)
        card.pack(side="left", padx=(0, 14))
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=icon if unlocked else "🔒",
            font=ctk.CTkFont(size=30),
        ).pack(pady=(18, 4))

        ctk.CTkLabel(
            card,
            text=title,
            text_color=title_color,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            card,
            text=desc,
            text_color=desc_color,
            font=ctk.CTkFont(size=12),
            wraplength=180,
            justify="center",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            card,
            text=badge_text,
            text_color=badge_color,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).pack(pady=(0, 12))

    def _import_quiz(self):
        root = self.winfo_toplevel()
        import_window = ctk.CTkToplevel(root)
        import_window.title("Import Quiz")
        import_window.geometry("560x460")
        import_window.configure(fg_color=MAIN_BG)
        import_window.grab_set()

        ctk.CTkLabel(
            import_window,
            text="Import Quiz Questions",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(28, 4))

        ctk.CTkLabel(
            import_window,
            text="Upload a CSV file containing your True / False questions.",
            text_color="#64748B",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=30, pady=(0, 18))

        # Format card
        format_card = ctk.CTkFrame(import_window, fg_color=CARD, corner_radius=14)
        format_card.pack(fill="x", padx=30, pady=(0, 18))

        ctk.CTkLabel(
            format_card,
            text="Required CSV Format",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            format_card,
            text=(
                "• First row must be a header: question,answer\n"
                "• 'answer' column must be either True or False\n"
                "• One question per row, no blank lines"
            ),
            text_color="#475569",
            font=ctk.CTkFont(size=13),
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        example = (
            "question,answer\n"
            "Python is a programming language,True\n"
            "HTML is a database,False"
        )
        ctk.CTkLabel(
            format_card,
            text=example,
            text_color=TEXT_DARK,
            fg_color="#F1F5F9",
            corner_radius=8,
            font=ctk.CTkFont(family="Menlo", size=12),
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 16), ipadx=10, ipady=10)

        # File picker row
        picker = ctk.CTkFrame(import_window, fg_color="transparent")
        picker.pack(fill="x", padx=30, pady=(0, 4))

        file_label = ctk.CTkLabel(
            picker,
            text="No file selected",
            text_color="#64748B",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        file_label.pack(side="left", fill="x", expand=True)

        status_label = ctk.CTkLabel(
            import_window,
            text="",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        status_label.pack(fill="x", padx=30, pady=(0, 8))

        selected = {"questions": None}

        def _browse():
            path = filedialog.askopenfilename(
                parent=import_window,
                title="Select questions CSV",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
            if not path:
                return

            file_label.configure(
                text=os.path.basename(path), text_color=TEXT_DARK
            )

            try:
                parsed = parse_questions_csv(path)
            except (ValueError, OSError, UnicodeDecodeError) as e:
                selected["questions"] = None
                status_label.configure(text=f"⚠ {e}", text_color="#DC2626")
                return

            selected["questions"] = parsed
            status_label.configure(
                text=f"✓ {len(parsed)} questions ready to import",
                text_color="#16A34A",
            )

        ctk.CTkButton(
            picker,
            text="Browse File",
            width=140,
            height=38,
            fg_color=PRIMARY,
            command=_browse,
        ).pack(side="right")

        def _on_import():
            if not selected["questions"]:
                messagebox.showerror(
                    "Import",
                    "Please select a valid CSV file first.",
                    parent=import_window,
                )
                return

            self.questions = selected["questions"]
            self.current_index = 0
            self.score = 0
            import_window.destroy()
            self._show_question()

        # Footer actions
        footer = ctk.CTkFrame(import_window, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=30, pady=20)

        ctk.CTkButton(
            footer,
            text="Cancel",
            width=120,
            height=40,
            fg_color="#E2E8F0",
            text_color=TEXT_DARK,
            hover_color="#CBD5E1",
            command=import_window.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            footer,
            text="Import & Start",
            width=160,
            height=40,
            fg_color=PRIMARY,
            command=_on_import,
        ).pack(side="right")


    def _show_profile_page(self):
        self._clear_main_content()

        stats = get_user_stats(self.current_user)

        scroll = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            scroll,
            text="Profile",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            scroll,
            text=f"@{self.current_user}",
            text_color="#64748B",
            font=ctk.CTkFont(size=16),
        ).pack(anchor="w", pady=(6, 22))

        # Member Since + Rank row
        info_row = ctk.CTkFrame(scroll, fg_color="transparent")
        info_row.pack(anchor="w", fill="x", pady=(0, 22))

        member_since = (
            stats["first_date"].strftime("%B %Y") if stats["first_date"] else "—"
        )
        rank_name, rank_color, rank_icon = self._get_rank(stats)

        self._info_card(info_row, "Member Since", member_since, "📅", TEXT_DARK)
        self._info_card(info_row, "Rank", rank_name, rank_icon, rank_color)

        # Quiz Statistics
        ctk.CTkLabel(
            scroll,
            text="Quiz Statistics",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", pady=(4, 12))

        stats_row = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_row.pack(anchor="w", fill="x", pady=(0, 22))

        accuracy_text = (
            f"{stats['accuracy']:.1f}%" if stats["total_questions"] else "0.0%"
        )
        self._stat_card(stats_row, "Total Attempts", str(stats["attempts"]), "📚")
        self._stat_card(
            stats_row, "Correct Answers", str(stats["total_correct"]), "✅"
        )
        self._stat_card(stats_row, "Overall Accuracy", accuracy_text, "🎯")

        # Achievements
        ctk.CTkLabel(
            scroll,
            text="Achievements",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(anchor="w", pady=(4, 12))

        ach_row = ctk.CTkFrame(scroll, fg_color="transparent")
        ach_row.pack(anchor="w", fill="x", pady=(0, 22))

        for icon, title, desc, unlocked in self._get_achievements(stats):
            self._achievement_card(ach_row, icon, title, desc, unlocked)

        ctk.CTkButton(
            scroll,
            text="Back to Dashboard",
            width=220,
            height=42,
            command=self._show_dashboard_page,
        ).pack(anchor="w", pady=(8, 20))

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

    def _show_create_flashcard(self):
        self._clear_main_content()
        FlashcardPanel(
            self.main,
            username=self.current_user,
            fg_color="transparent",
        ).pack(fill="both", expand=True)

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
