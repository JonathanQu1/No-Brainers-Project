from zipapp import create_archive
import customtkinter as ctk
from tkinter import messagebox

from frontend.quiz import load_questions
from frontend.user_store import (
    delete_set,
    get_attempt_count,
    get_last_score,
    get_set_flashcards,
    get_set_names,
    save_flashcard,
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
            text="Start Quiz",
            width=165,
            height=40,
            command=self._start_quiz,
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

    def _show_create_flashcard(self):
        self._clear_main_content()
        #========Tab Colors=========
        #Fix the colors
        notebook = ctk.CTkTabview(
            self.main,
            anchor="nw",
            fg_color="#FFFFFF",
            segmented_button_fg_color="#FFFFFF",
            segmented_button_selected_color=PRIMARY,
            segmented_button_selected_hover_color="#1D4ED8",
            segmented_button_unselected_color=PRIMARY,
            segmented_button_unselected_hover_color="#1D4ED8",
            text_color="#FFFFFF",
            text_color_disabled="#64748B",
        )
        notebook.pack(fill="both", expand=True)


        #============Create a Set============
        create_set_frame = notebook.add("Create Set")

        ctk.CTkLabel(
            create_set_frame,
            text="Create a flashcard set",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(18, 16))

        ctk.CTkLabel(create_set_frame, text="Set name").pack(anchor="w", padx=20)
        self.set_name_entry = ctk.CTkEntry(
            create_set_frame, width=420, placeholder_text="e.g. Biology Basics"
        )
        self.set_name_entry.pack(anchor="w", padx=20, pady=(5, 12))

        ctk.CTkLabel(create_set_frame, text="Term").pack(anchor="w", padx=20)
        self.card_term_entry = ctk.CTkEntry(
            create_set_frame, width=540, placeholder_text="Question or term"
        )
        self.card_term_entry.pack(anchor="w", padx=20, pady=(5, 12))

        ctk.CTkLabel(create_set_frame, text="Definition").pack(anchor="w", padx=20)
        self.card_definition_entry = ctk.CTkEntry(
            create_set_frame, width=540, placeholder_text="Answer or definition"
        )
        self.card_definition_entry.pack(anchor="w", padx=20, pady=(5, 16))

        action_row = ctk.CTkFrame(create_set_frame, fg_color="transparent")
        action_row.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkButton(
            action_row,
            text="Save Card",
            fg_color=PRIMARY,
            command=self._save_current_flashcard,
        ).pack(side="left")

        ctk.CTkButton(
            action_row,
            text="Clear",
            fg_color="#64748B",
            hover_color="#475569",
            command=self._clear_flashcard_form,
        ).pack(side="left", padx=10)

        self.create_set_status = ctk.CTkLabel(create_set_frame, text="", text_color="#16A34A")
        self.create_set_status.pack(anchor="w", padx=20, pady=(2, 0))


        #============Select a Set============
        select_set_frame = notebook.add("Select Set")
        ctk.CTkLabel(
            select_set_frame,
            text="Browse your sets",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(18, 16))

        self.selected_set_var = ctk.StringVar(value="No sets yet")
        self.select_set_menu = ctk.CTkOptionMenu(
            select_set_frame,
            values=["No sets yet"],
            variable=self.selected_set_var,
            width=300,
            command=lambda _choice: self._render_selected_set_cards(),
        )
        self.select_set_menu.pack(anchor="w", padx=20, pady=(0, 12))

        ctk.CTkButton(
            select_set_frame,
            text="Refresh Sets",
            fg_color=PRIMARY,
            command=self._refresh_set_menu,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        ctk.CTkButton(
            select_set_frame,
            text="Delete Set",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self._delete_selected_set,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        self.set_cards_box = ctk.CTkTextbox(select_set_frame, width=650, height=260)
        self.set_cards_box.pack(anchor="w", padx=20, pady=(0, 12))
        self.set_cards_box.insert("1.0", "No set selected.")
        self.set_cards_box.configure(state="disabled")


        #============Learn Mode============
        learn_mode_frame = notebook.add("Learn Mode")

        ctk.CTkLabel(
            learn_mode_frame,
            text="Learn mode",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(18, 16))
        ctk.CTkLabel(
            learn_mode_frame,
            text="Choose a set, then flip cards and move previous/next.",
            text_color="#64748B",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=20, pady=(0, 12))

        self.learn_set_var = ctk.StringVar(value="No sets yet")
        self.learn_set_menu = ctk.CTkOptionMenu(
            learn_mode_frame,
            values=["No sets yet"],
            variable=self.learn_set_var,
            width=300,
        )
        self.learn_set_menu.pack(anchor="w", padx=20, pady=(0, 12))

        ctk.CTkButton(
            learn_mode_frame,
            text="Load Set",
            fg_color=PRIMARY,
            command=self._start_learn_mode,
        ).pack(anchor="w", padx=20, pady=(0, 14))

        self.learn_cards = []
        self.learn_index = 0
        self.learn_showing_back = False

        self._refresh_set_menu()



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

    def _clear_flashcard_form(self):
        if hasattr(self, "set_name_entry"):
            self.set_name_entry.delete(0, "end")
        if hasattr(self, "card_term_entry"):
            self.card_term_entry.delete(0, "end")
        if hasattr(self, "card_definition_entry"):
            self.card_definition_entry.delete(0, "end")
        if hasattr(self, "create_set_status"):
            self.create_set_status.configure(text="")

    def _save_current_flashcard(self):
        set_name = self.set_name_entry.get().strip()
        term = self.card_term_entry.get().strip()
        definition = self.card_definition_entry.get().strip()

        if not set_name:
            messagebox.showerror("Missing Set Name", "Please enter a set name.")
            return
        if not term or not definition:
            messagebox.showerror(
                "Missing Card Content", "Please fill both Term and Definition."
            )
            return

        save_flashcard(self.current_user, set_name, term, definition)
        self.create_set_status.configure(text=f'Saved card to set "{set_name}".')
        self.card_term_entry.delete(0, "end")
        self.card_definition_entry.delete(0, "end")
        self._refresh_set_menu(default_set_name=set_name)

    def _refresh_set_menu(self, default_set_name=None):
        set_names = get_set_names(self.current_user)
        if not set_names:
            self.select_set_menu.configure(values=["No sets yet"])
            self.selected_set_var.set("No sets yet")
            if hasattr(self, "learn_set_menu"):
                self.learn_set_menu.configure(values=["No sets yet"])
                self.learn_set_var.set("No sets yet")
            self._update_set_cards_box("No sets yet. Add a card in Create Set.")
            return

        self.select_set_menu.configure(values=set_names)
        if hasattr(self, "learn_set_menu"):
            self.learn_set_menu.configure(values=set_names)
        if default_set_name and default_set_name in set_names:
            self.selected_set_var.set(default_set_name)
            if hasattr(self, "learn_set_var"):
                self.learn_set_var.set(default_set_name)
        elif self.selected_set_var.get() not in set_names:
            self.selected_set_var.set(set_names[0])
            if hasattr(self, "learn_set_var"):
                self.learn_set_var.set(set_names[0])
        self._render_selected_set_cards()

    def _render_selected_set_cards(self):
        selected = self.selected_set_var.get().strip()
        if not selected or selected == "No sets yet":
            self._update_set_cards_box("No set selected.")
            return

        cards = get_set_flashcards(self.current_user, selected)
        if not cards:
            self._update_set_cards_box("This set has no cards.")
            return

        lines = [f"Set: {selected}", ""]
        for i, card in enumerate(cards, start=1):
            lines.append(f"{i}. Term: {card['term']}")
            lines.append(f"   Definition: {card['definition']}")
            lines.append("")
        self._update_set_cards_box("\n".join(lines).strip())

    def _update_set_cards_box(self, text):
        self.set_cards_box.configure(state="normal")
        self.set_cards_box.delete("1.0", "end")
        self.set_cards_box.insert("1.0", text)
        self.set_cards_box.configure(state="disabled")

    def _delete_selected_set(self):
        selected = self.selected_set_var.get().strip()
        if not selected or selected == "No sets yet":
            messagebox.showerror("No Set Selected", "Choose a set to delete.")
            return

        confirmed = messagebox.askyesno(
            "Delete Set",
            f'Are you sure you want to delete "{selected}"?\nThis removes all cards in this set.',
        )
        if not confirmed:
            return

        delete_set(self.current_user, selected)
        self._refresh_set_menu()
        self._update_set_cards_box("Set deleted.")

    def _start_learn_mode(self):
        selected = self.learn_set_var.get().strip()
        if not selected or selected == "No sets yet":
            messagebox.showerror("No Set Selected", "Choose a set to start Learn Mode.")
            return

        cards = get_set_flashcards(self.current_user, selected)
        if not cards:
            messagebox.showerror("Empty Set", "This set does not contain cards yet.")
            return

        self.learn_cards = cards
        self.learn_index = 0
        self.learn_showing_back = False
        self._open_learn_mode_window(selected)
        self._render_learn_card()

    def _open_learn_mode_window(self, set_name):
        if hasattr(self, "learn_window") and self.learn_window is not None:
            try:
                if self.learn_window.winfo_exists():
                    self.learn_window.destroy()
            except Exception:
                pass

        self.learn_window = ctk.CTkToplevel(self.winfo_toplevel())
        self.learn_window.title(f"Learn Mode - {set_name}")
        self.learn_window.geometry("760x520")
        self.learn_window.grab_set()

        ctk.CTkLabel(
            self.learn_window,
            text=f'{set_name}',
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="n", padx=24, pady=(20, 10))

        self.learn_window_progress_label = ctk.CTkLabel(
            self.learn_window,
            text="Card 1/1",
            text_color="#64748B",
            font=ctk.CTkFont(size=14),
        )
        self.learn_window_progress_label.pack(anchor="w", padx=24, pady=(0, 10))

        card_frame = ctk.CTkFrame(
            self.learn_window, fg_color=CARD, corner_radius=16, width=700, height=280
        )
        card_frame.pack(anchor="center", padx=24, pady=(0, 16), fill="x")
        card_frame.pack_propagate(False)

        self.learn_window_side_label = ctk.CTkLabel(
            card_frame,
            text="Term",
            text_color="#64748B",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.learn_window_side_label.pack(pady=(26, 8))

        self.learn_window_card_text = ctk.CTkLabel(
            card_frame,
            text="",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
            wraplength=640,
            justify="center",
        )
        self.learn_window_card_text.pack(expand=True, padx=20, pady=(0, 24))

        controls = ctk.CTkFrame(self.learn_window, fg_color="transparent")
        controls.pack(pady=(0, 20))

        ctk.CTkButton(
            controls,
            text="Previous",
            fg_color="#64748B",
            hover_color="#475569",
            command=self._learn_prev,
        ).pack(side="left")

        ctk.CTkButton(
            controls,
            text="Flip",
            fg_color=PRIMARY,
            command=self._learn_flip,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            controls,
            text="Next",
            fg_color="#64748B",
            hover_color="#475569",
            command=self._learn_next,
        ).pack(side="left")

    def _render_learn_card(self):
        if not self.learn_cards:
            return

        card = self.learn_cards[self.learn_index]
        side_label = "Definition" if self.learn_showing_back else "Term"
        text = card["definition"] if self.learn_showing_back else card["term"]
        if hasattr(self, "learn_window") and self.learn_window is not None:
            try:
                if self.learn_window.winfo_exists():
                    self.learn_window_progress_label.configure(
                        text=f"{self.learn_index + 1}/{len(self.learn_cards)}"
                    )
                    self.learn_window_side_label.configure(text=side_label)
                    self.learn_window_card_text.configure(text=text)
            except Exception:
                pass

    def _learn_flip(self):
        if not self.learn_cards:
            return
        self.learn_showing_back = not self.learn_showing_back
        self._render_learn_card()

    def _learn_prev(self):
        if not self.learn_cards:
            return
        self.learn_index = (self.learn_index - 1) % len(self.learn_cards)
        self.learn_showing_back = False
        self._render_learn_card()

    def _learn_next(self):
        if not self.learn_cards:
            return
        self.learn_index = (self.learn_index + 1) % len(self.learn_cards)
        self.learn_showing_back = False
        self._render_learn_card()

    def _on_logout_click(self):
        if self.on_logout is not None:
            self.on_logout()
