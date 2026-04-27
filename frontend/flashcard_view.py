import customtkinter as ctk
from tkinter import messagebox

from frontend.user_store import (
    delete_set,
    get_set_flashcards,
    get_set_names,
    save_flashcard,
)

CARD = "#FFFFFF"
PRIMARY = "#2563EB"
TEXT_DARK = "#0F172A"


class FlashcardPanel(ctk.CTkFrame):

    def __init__(self, parent, username: str, **kwargs):
        super().__init__(parent, **kwargs)
        # Keep the logged-in user so all flashcard actions stay user-specific.
        self.username = username
        # Learn Mode state (which cards are loaded and what side is showing).
        self.learn_cards = []
        self.learn_index = 0
        self.learn_showing_back = False
        self.learn_window = None
        self._build()

    def _build(self):
        # Main tab container for all flashcard workflows.
        notebook = ctk.CTkTabview(
            self,
            anchor="nw",
            fg_color=CARD,
            segmented_button_fg_color=CARD,
            segmented_button_selected_color=PRIMARY,
            segmented_button_selected_hover_color="#1D4ED8",
            segmented_button_unselected_color=PRIMARY,
            segmented_button_unselected_hover_color="#1D4ED8",
            text_color=CARD,
            text_color_disabled="#64748B",
        )
        notebook.pack(fill="both", expand=True)

        # Tab 1: create and save cards into a set.
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

        self.create_set_status = ctk.CTkLabel(
            create_set_frame, text="", text_color="#16A34A"
        )
        self.create_set_status.pack(anchor="w", padx=20, pady=(2, 0))

        # Tab 2: browse existing sets and optionally delete one.
        select_set_frame = notebook.add("Select Set")
        ctk.CTkLabel(
            select_set_frame,
            text="Browse your sets",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(18, 16))

        menu_row = ctk.CTkFrame(select_set_frame, fg_color="transparent")
        menu_row.pack(anchor="w", padx=20, pady=(0, 12))

        self.selected_set_var = ctk.StringVar(value="No sets yet")
        self.select_set_menu = ctk.CTkOptionMenu(
            menu_row,
            values=["No sets yet"],
            variable=self.selected_set_var,
            width=300,
            command=lambda _choice: self._render_selected_set_cards(),
        )
        self.select_set_menu.pack(side="left")

        ctk.CTkButton(
            menu_row,
            text="↻",
            width=40,
            height=30,
            fg_color=PRIMARY,
            command=self._refresh_set_menu,
        ).pack(side="left", padx=(10, 0))

        ctk.CTkButton(
            menu_row,
            text="🗑️",
            fg_color=("gray85", "gray25"),
            hover_color=("gray75", "gray35"),
            width=40,
            height=30,
            command=self._delete_selected_set,
        ).pack(side="left", padx=(10, 0))

        self.set_preview_name = ctk.CTkLabel(
            select_set_frame,
            text="",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.set_preview_name.pack(anchor="w", padx=20, pady=(4, 6))

        self.set_cards_scroll = ctk.CTkScrollableFrame(
            select_set_frame,
            width=650,
            height=260,
            fg_color="transparent",
        )
        self.set_cards_scroll.pack(
            anchor="w", fill="both", expand=True, padx=20, pady=(0, 12)
        )
        self._show_set_preview_message("No set selected.")

        # Tab 3: quick study mode (flip through cards in a popup window).
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
            text="Start Learning",
            fg_color=PRIMARY,
            command=self._start_learn_mode,
        ).pack(anchor="w", padx=20, pady=(0, 14))

        self._refresh_set_menu()

    def _clear_flashcard_form(self):
        # Reset form fields and any green success message.
        self.set_name_entry.delete(0, "end")
        self.card_term_entry.delete(0, "end")
        self.card_definition_entry.delete(0, "end")
        self.create_set_status.configure(text="")

    def _save_current_flashcard(self):
        # Read current form inputs.
        set_name = self.set_name_entry.get().strip()
        term = self.card_term_entry.get().strip()
        definition = self.card_definition_entry.get().strip()

        # Basic validation before writing to storage.
        if not set_name:
            messagebox.showerror("Missing Set Name", "Please enter a set name.")
            return
        if not term or not definition:
            messagebox.showerror(
                "Missing Card Content", "Please fill both Term and Definition."
            )
            return

        # Save card, show confirmation, clear card inputs, then refresh menus.
        save_flashcard(self.username, set_name, term, definition)
        self.create_set_status.configure(text=f'Saved card to set "{set_name}".')
        self.card_term_entry.delete(0, "end")
        self.card_definition_entry.delete(0, "end")
        self._refresh_set_menu(default_set_name=set_name)

    def _refresh_set_menu(self, default_set_name=None):
        # Rebuild set dropdown options from storage.
        set_names = get_set_names(self.username)
        if not set_names:
            # Empty state for both dropdowns and the preview box.
            self.select_set_menu.configure(values=["No sets yet"])
            self.selected_set_var.set("No sets yet")
            self.learn_set_menu.configure(values=["No sets yet"])
            self.learn_set_var.set("No sets yet")
            self._show_set_preview_message("No sets yet. Add a card in Create Set.")
            return

        # Keep both dropdowns aligned and pick a sensible selected set.
        self.select_set_menu.configure(values=set_names)
        self.learn_set_menu.configure(values=set_names)
        if default_set_name and default_set_name in set_names:
            self.selected_set_var.set(default_set_name)
            self.learn_set_var.set(default_set_name)
        elif self.selected_set_var.get() not in set_names:
            self.selected_set_var.set(set_names[0])
            self.learn_set_var.set(set_names[0])
        self._render_selected_set_cards()

    def _clear_set_cards_scroll(self):
        for child in self.set_cards_scroll.winfo_children():
            child.destroy()

    def _show_set_preview_message(self, message: str):
        # Empty / info state: hide the set title and show a single message.
        self.set_preview_name.configure(text="")
        self._clear_set_cards_scroll()
        ctk.CTkLabel(
            self.set_cards_scroll,
            text=message,
            text_color="#64748B",
            font=ctk.CTkFont(size=14),
            wraplength=620,
            justify="left",
        ).pack(anchor="w", padx=4, pady=8)

    def _render_selected_set_cards(self):
        # Show set name plus a two-column Term | Definition list (no numbering).
        selected = self.selected_set_var.get().strip()
        if not selected or selected == "No sets yet":
            self._show_set_preview_message("No set selected.")
            return

        cards = get_set_flashcards(self.username, selected)
        self.set_preview_name.configure(text=selected)
        self._clear_set_cards_scroll()

        if not cards:
            ctk.CTkLabel(
                self.set_cards_scroll,
                text="This set has no cards.",
                text_color="#64748B",
                font=ctk.CTkFont(size=14),
            ).pack(anchor="w", padx=4, pady=8)
            return

        header = ctk.CTkFrame(
            self.set_cards_scroll, fg_color="#E2E8F0", corner_radius=8
        )
        header.pack(fill="x", pady=(0, 8))
        header.grid_columnconfigure(0, weight=1, uniform="setpair")
        header.grid_columnconfigure(1, weight=1, uniform="setpair")

        ctk.CTkLabel(
            header,
            text="Term",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=10)
        ctk.CTkLabel(
            header,
            text="Definition",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=14, pady=10)

        for card in cards:
            row = ctk.CTkFrame(
                self.set_cards_scroll, fg_color="#F8FAFC", corner_radius=8
            )
            row.pack(fill="x", pady=(0, 6))
            row.grid_columnconfigure(0, weight=1, uniform="setpair")
            row.grid_columnconfigure(1, weight=1, uniform="setpair")

            term = (card.get("term") or "").strip()
            definition = (card.get("definition") or "").strip()

            ctk.CTkLabel(
                row,
                text=term,
                text_color=TEXT_DARK,
                font=ctk.CTkFont(size=14),
                wraplength=300,
                justify="left",
                anchor="w",
            ).grid(row=0, column=0, sticky="nw", padx=14, pady=10)
            ctk.CTkLabel(
                row,
                text=definition,
                text_color=TEXT_DARK,
                font=ctk.CTkFont(size=14),
                wraplength=300,
                justify="left",
                anchor="w",
            ).grid(row=0, column=1, sticky="nw", padx=14, pady=10)

    def _delete_selected_set(self):
        # Delete currently selected set after user confirmation.
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

        delete_set(self.username, selected)
        self._refresh_set_menu()
        self._show_set_preview_message("Set deleted.")

    def _start_learn_mode(self):
        # Load cards for Learn Mode and open the study popup.
        selected = self.learn_set_var.get().strip()
        if not selected or selected == "No sets yet":
            messagebox.showerror("No Set Selected", "Choose a set to start Learn Mode.")
            return

        cards = get_set_flashcards(self.username, selected)
        if not cards:
            messagebox.showerror("Empty Set", "This set does not contain cards yet.")
            return

        self.learn_cards = cards
        self.learn_index = 0
        self.learn_showing_back = False
        self._open_learn_mode_window(selected)
        self._render_learn_card()

    def _open_learn_mode_window(self, set_name):
        # Close any existing Learn Mode window before opening a fresh one.
        if self.learn_window is not None:
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
            text=f"{set_name}",
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
        # Draw current card face (term/definition) and progress label.
        if not self.learn_cards:
            return

        card = self.learn_cards[self.learn_index]
        side_label = "Definition" if self.learn_showing_back else "Term"
        text = card["definition"] if self.learn_showing_back else card["term"]
        if self.learn_window is not None:
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
        # Toggle between term and definition on the current card.
        if not self.learn_cards:
            return
        self.learn_showing_back = not self.learn_showing_back
        self._render_learn_card()

    def _learn_prev(self):
        # Move to previous card (wrap around) and reset to term side.
        if not self.learn_cards:
            return
        self.learn_index = (self.learn_index - 1) % len(self.learn_cards)
        self.learn_showing_back = False
        self._render_learn_card()

    def _learn_next(self):
        # Move to next card (wrap around) and reset to term side.
        if not self.learn_cards:
            return
        self.learn_index = (self.learn_index + 1) % len(self.learn_cards)
        self.learn_showing_back = False
        self._render_learn_card()
