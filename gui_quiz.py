#!/usr/bin/env python3
"""Geography quiz desktop UI (tkinter)."""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Callable


try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
except ImportError as exc:
    if getattr(exc, "name", None) == "_tkinter" or "_tkinter" in str(exc):
        print(
            "Tk is not available for this Python build (common with Homebrew Python).\n\n"
            "Fix (Homebrew, match your Python version):\n"
            "  brew install python-tk@3.14\n\n"
            "Or install Python from https://www.python.org/downloads/ (includes Tk).\n\n"
            "CLI quiz (no GUI): python3 run_quiz.py",
            file=sys.stderr,
        )
    else:
        print(f"Could not import tkinter: {exc}", file=sys.stderr)
    raise SystemExit(1) from exc

from quiz_engine import (
    list_quiz_paths,
    load_quiz,
    prepare_questions,
    read_quiz_title,
    save_quiz,
    validate_question_dict,
    validate_quiz_file,
)

_FAMILY = "Helvetica Neue" if sys.platform == "darwin" else "DejaVu Sans"

# Calm slate + sky accent (reads well on Retina, not generic “AI purple”)
_COLORS = {
    "app_bg": "#eef2f6",
    "header_bg": "#0f172a",
    "header_fg": "#f8fafc",
    "header_muted": "#94a3b8",
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "text": "#0f172a",
    "muted": "#64748b",
    "accent": "#0284c7",
    "accent_active": "#0369a1",
    "success": "#059669",
    "error": "#dc2626",
    "ghost_border": "#cbd5e1",
    "ghost_hover": "#f1f5f9",
}

_TITLE = (_FAMILY, 20, "bold")
_SUBTITLE = (_FAMILY, 12)
_BODY_STRONG = (_FAMILY, 14, "bold")
_CHOICE = (_FAMILY, 13)
_CAPTION = (_FAMILY, 11)
_FEEDBACK = (_FAMILY, 13)
_SCORE = (_FAMILY, 28, "bold")
_BTN_PRIMARY = (_FAMILY, 13, "bold")
_BTN_SECONDARY = (_FAMILY, 12)


def _safe_quiz_filename(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return "my_quiz.json"
    base = raw.removesuffix(".json")
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", base).strip("._-")
    if not slug:
        slug = "my_quiz"
    return f"{slug}.json"


class CreateQuizDialog:
    """Modal window to build a quiz and save it under ``data_dir``."""

    def __init__(
        self,
        parent: tk.Tk,
        data_dir: Path,
        on_saved: Callable[[Path], None],
    ) -> None:
        self.data_dir = data_dir
        self.on_saved = on_saved
        self.questions: list[dict] = []

        self.win = tk.Toplevel(parent)
        self.win.title("Create a quiz")
        self.win.configure(bg=_COLORS["card_bg"])
        self.win.transient(parent)
        self.win.grab_set()
        self.win.minsize(560, 620)

        self.correct_var = tk.IntVar(value=0)

        pad = {"padx": 20, "pady": 8}
        tk.Label(self.win, text="Quiz title", font=_BODY_STRONG, bg=_COLORS["card_bg"], fg=_COLORS["text"]).pack(
            anchor="w", **pad
        )
        self.title_entry = tk.Entry(self.win, font=_CHOICE, width=50, relief=tk.FLAT, highlightthickness=1, highlightbackground=_COLORS["ghost_border"])
        self.title_entry.pack(fill=tk.X, padx=20, pady=(0, 12))

        tk.Label(self.win, text="Question", font=_BODY_STRONG, bg=_COLORS["card_bg"], fg=_COLORS["text"]).pack(
            anchor="w", padx=20, pady=(4, 4)
        )
        self.question_text = tk.Text(self.win, height=3, width=50, font=_CHOICE, relief=tk.FLAT, highlightthickness=1, highlightbackground=_COLORS["ghost_border"], wrap=tk.WORD)
        self.question_text.pack(fill=tk.X, padx=20, pady=(0, 8))

        self.choice_entries: list[tk.Entry] = []
        for i in range(4):
            row = tk.Frame(self.win, bg=_COLORS["card_bg"])
            row.pack(fill=tk.X, padx=20, pady=4)
            tk.Label(row, text=f"Choice {i + 1}", font=_CAPTION, bg=_COLORS["card_bg"], fg=_COLORS["muted"], width=10, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(row, font=_CHOICE, relief=tk.FLAT, highlightthickness=1, highlightbackground=_COLORS["ghost_border"])
            e.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.choice_entries.append(e)

        tk.Label(self.win, text="Correct answer", font=_BODY_STRONG, bg=_COLORS["card_bg"], fg=_COLORS["text"]).pack(
            anchor="w", padx=20, pady=(12, 4)
        )
        rb_row = tk.Frame(self.win, bg=_COLORS["card_bg"])
        rb_row.pack(anchor="w", padx=20)
        for i in range(4):
            tk.Radiobutton(
                rb_row,
                text=str(i + 1),
                variable=self.correct_var,
                value=i,
                font=_CHOICE,
                bg=_COLORS["card_bg"],
                fg=_COLORS["text"],
                activebackground=_COLORS["card_bg"],
                highlightthickness=0,
            ).pack(side=tk.LEFT, padx=(0, 12))

        mid = tk.Frame(self.win, bg=_COLORS["card_bg"])
        mid.pack(fill=tk.X, padx=20, pady=16)
        tk.Button(
            mid,
            text="Add to quiz",
            font=_BTN_PRIMARY,
            bg=_COLORS["accent"],
            fg="#ffffff",
            activebackground=_COLORS["accent_active"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=18,
            pady=8,
            cursor="hand2",
            bd=0,
            command=self._add_question,
        ).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(
            mid,
            text="Clear form",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            relief=tk.FLAT,
            padx=16,
            pady=8,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            cursor="hand2",
            command=self._clear_form,
        ).pack(side=tk.LEFT)

        self.count_label = tk.Label(
            self.win,
            text="Questions in this quiz: 0",
            font=_CAPTION,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            anchor="w",
        )
        self.count_label.pack(anchor="w", padx=20, pady=(0, 6))

        list_frame = tk.Frame(self.win, bg=_COLORS["card_bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 12))
        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(
            list_frame,
            height=6,
            font=_CHOICE,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            yscrollcommand=scroll.set,
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.listbox.yview)

        tk.Button(
            self.win,
            text="Remove selected",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            relief=tk.FLAT,
            padx=12,
            pady=6,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            cursor="hand2",
            command=self._remove_selected,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        bottom = tk.Frame(self.win, bg=_COLORS["card_bg"])
        bottom.pack(fill=tk.X, padx=20, pady=(0, 20))
        tk.Button(
            bottom,
            text="Save quiz",
            font=_BTN_PRIMARY,
            bg=_COLORS["success"],
            fg="#ffffff",
            activebackground="#047857",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=22,
            pady=10,
            cursor="hand2",
            bd=0,
            command=self._save,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            bottom,
            text="Cancel",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            relief=tk.FLAT,
            padx=18,
            pady=10,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            cursor="hand2",
            command=self.win.destroy,
        ).pack(side=tk.LEFT)

        self._center_on_parent(parent)

    def _center_on_parent(self, parent: tk.Tk) -> None:
        self.win.update_idletasks()
        w, h = 600, 640
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 3)
        self.win.geometry(f"{w}x{h}+{x}+{y}")

    def _clear_form(self) -> None:
        self.question_text.delete("1.0", tk.END)
        for e in self.choice_entries:
            e.delete(0, tk.END)
        self.correct_var.set(0)

    def _current_form_question(self) -> dict | None:
        qtext = self.question_text.get("1.0", tk.END).strip()
        choices = [e.get().strip() for e in self.choice_entries]
        ci = self.correct_var.get()
        try:
            draft = {"question": qtext, "choices": choices, "correct_index": ci}
            validate_question_dict(draft)
        except (ValueError, KeyError) as e:
            messagebox.showwarning("Check fields", str(e), parent=self.win)
            return None
        return {"question": draft["question"], "choices": draft["choices"], "correct_index": draft["correct_index"]}

    def _add_question(self) -> None:
        q = self._current_form_question()
        if q is None:
            return
        self.questions.append(q)
        preview = q["question"][:72] + ("…" if len(q["question"]) > 72 else "")
        self.listbox.insert(tk.END, preview)
        self.count_label.config(text=f"Questions in this quiz: {len(self.questions)}")
        self._clear_form()

    def _remove_selected(self) -> None:
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Remove", "Select a question in the list first.", parent=self.win)
            return
        i = int(sel[0])
        self.listbox.delete(i)
        del self.questions[i]
        self.count_label.config(text=f"Questions in this quiz: {len(self.questions)}")

    def _save(self) -> None:
        if not self.questions:
            messagebox.showwarning("No questions", "Add at least one question before saving.", parent=self.win)
            return
        title = self.title_entry.get().strip() or "Untitled quiz"
        default_name = _safe_quiz_filename(title).replace(".json", "")
        name = simpledialog.askstring(
            "Save quiz",
            "File name (saved as .json in the data folder):",
            initialvalue=default_name,
            parent=self.win,
        )
        if name is None:
            return
        filename = _safe_quiz_filename(name)
        path = self.data_dir / filename
        if path.exists():
            if not messagebox.askyesno("Overwrite", f"Replace existing file?\n{path.name}", parent=self.win):
                return
        try:
            save_quiz(path, title, self.questions)
        except ValueError as e:
            messagebox.showerror("Could not save", str(e), parent=self.win)
            return
        messagebox.showinfo("Saved", f"Quiz saved as:\n{path.name}", parent=self.win)
        self.on_saved(path)
        self.win.destroy()


class QuizApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("No-Brainers Quiz")
        self.root.minsize(520, 460)
        self.root.configure(bg=_COLORS["app_bg"])
        self.data_dir = Path(__file__).resolve().parent / "data"
        self.active_quiz_path: Path | None = None

        self.choice_var = tk.IntVar(value=-1)
        self.choices_frame: tk.Frame | None = None

        self._build_chrome()
        self._place_window()
        self._bind_wraplength()
        self.show_launcher()

    def _place_window(self) -> None:
        self.root.update_idletasks()
        w, h = 580, 520
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 3)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _bind_wraplength(self) -> None:
        def on_resize(_event: tk.Event) -> None:
            try:
                card_w = self.card.winfo_width()
                if card_w > 80:
                    self.question_label.configure(wraplength=max(280, card_w - 72))
            except tk.TclError:
                pass

        self.card.bind("<Configure>", on_resize)

    def _build_chrome(self) -> None:
        outer = tk.Frame(self.root, bg=_COLORS["app_bg"])
        outer.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(outer, bg=_COLORS["header_bg"], height=76)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        head_inner = tk.Frame(header, bg=_COLORS["header_bg"])
        head_inner.pack(fill=tk.BOTH, expand=True, padx=28, pady=(18, 16))

        self.header = tk.Label(
            head_inner,
            text="Quiz",
            bg=_COLORS["header_bg"],
            fg=_COLORS["header_fg"],
            font=_TITLE,
            anchor="w",
        )
        self.header.pack(anchor="w")

        self.header_tag = tk.Label(
            head_inner,
            text="Test your knowledge",
            bg=_COLORS["header_bg"],
            fg=_COLORS["header_muted"],
            font=_SUBTITLE,
            anchor="w",
        )
        self.header_tag.pack(anchor="w", pady=(4, 0))

        body = tk.Frame(outer, bg=_COLORS["app_bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        self.card = tk.Frame(
            body,
            bg=_COLORS["card_bg"],
            highlightbackground=_COLORS["card_border"],
            highlightthickness=1,
        )
        self.card.pack(fill=tk.BOTH, expand=True)

        self.inner = tk.Frame(self.card, bg=_COLORS["card_bg"])
        self.inner.pack(fill=tk.BOTH, expand=True, padx=28, pady=26)

        self.launcher_panel = tk.Frame(self.inner, bg=_COLORS["card_bg"])
        self.play_panel = tk.Frame(self.inner, bg=_COLORS["card_bg"])

        self._build_launcher(self.launcher_panel)
        self._build_play(self.play_panel)

    def _build_launcher(self, parent: tk.Frame) -> None:
        tk.Label(
            parent,
            text="Choose a quiz",
            font=_BODY_STRONG,
            bg=_COLORS["card_bg"],
            fg=_COLORS["text"],
            anchor="w",
        ).pack(anchor="w", fill=tk.X, pady=(0, 8))

        tk.Label(
            parent,
            text="Start a quiz from the list, create one, or import a JSON file from anywhere on your computer.",
            font=_CAPTION,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            anchor="w",
            wraplength=480,
            justify=tk.LEFT,
        ).pack(anchor="w", fill=tk.X, pady=(0, 12))

        list_frame = tk.Frame(parent, bg=_COLORS["card_bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        scroll = ttk.Scrollbar(list_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.quiz_listbox = tk.Listbox(
            list_frame,
            height=10,
            font=_CHOICE,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            yscrollcommand=scroll.set,
            selectmode=tk.SINGLE,
        )
        self.quiz_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.quiz_listbox.yview)

        self._quiz_paths: list[Path] = []

        row = tk.Frame(parent, bg=_COLORS["card_bg"])
        row.pack(fill=tk.X, pady=(8, 0))
        tk.Button(
            row,
            text="Start quiz",
            font=_BTN_PRIMARY,
            bg=_COLORS["accent"],
            fg="#ffffff",
            activebackground=_COLORS["accent_active"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=22,
            pady=10,
            cursor="hand2",
            bd=0,
            command=self._launcher_start,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            row,
            text="Create quiz",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["accent"],
            activebackground=_COLORS["ghost_hover"],
            activeforeground=_COLORS["accent_active"],
            relief=tk.FLAT,
            padx=18,
            pady=10,
            highlightthickness=1,
            highlightbackground=_COLORS["accent"],
            cursor="hand2",
            command=self._open_create_dialog,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            row,
            text="Import quiz…",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["text"],
            activebackground=_COLORS["ghost_hover"],
            activeforeground=_COLORS["text"],
            relief=tk.FLAT,
            padx=18,
            pady=10,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            cursor="hand2",
            command=self._import_quiz,
        ).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(
            row,
            text="Quit",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            activebackground=_COLORS["ghost_hover"],
            activeforeground=_COLORS["text"],
            relief=tk.FLAT,
            padx=18,
            pady=10,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            cursor="hand2",
            command=self.root.destroy,
        ).pack(side=tk.LEFT)

        self.quiz_listbox.bind("<Double-Button-1>", lambda _e: self._launcher_start())

    def _build_play(self, parent: tk.Frame) -> None:
        self.progress = tk.Label(
            parent,
            text="",
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            font=_CAPTION,
            anchor="w",
        )
        self.progress.pack(anchor="w", fill=tk.X, pady=(0, 12))

        self.question_label = tk.Label(
            parent,
            text="",
            bg=_COLORS["card_bg"],
            fg=_COLORS["text"],
            font=_BODY_STRONG,
            wraplength=480,
            justify=tk.LEFT,
            anchor="w",
        )
        self.question_label.pack(anchor="w", fill=tk.X, pady=(0, 18))

        self.choices_frame = tk.Frame(parent, bg=_COLORS["card_bg"])
        self.choices_frame.pack(anchor="w", fill=tk.X, pady=(0, 8))

        self.feedback = tk.Label(
            parent,
            text="",
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            font=_FEEDBACK,
            anchor="w",
            justify=tk.LEFT,
        )
        self.feedback.pack(anchor="w", fill=tk.X, pady=(12, 4))

        self.summary_hint = tk.Label(
            parent,
            text="",
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            font=_CAPTION,
            anchor="w",
        )
        self.summary_hint.pack(anchor="w", fill=tk.X, pady=(0, 16))

        self.btn_row = tk.Frame(parent, bg=_COLORS["card_bg"])
        self.btn_row.pack(anchor="w", fill=tk.X, pady=(8, 0))

        self.main_btn = tk.Button(
            self.btn_row,
            text="Submit",
            font=_BTN_PRIMARY,
            bg=_COLORS["accent"],
            fg="#ffffff",
            activebackground=_COLORS["accent_active"],
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=26,
            pady=11,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
        )
        self.main_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.menu_btn = tk.Button(
            self.btn_row,
            text="Main menu",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            activebackground=_COLORS["ghost_hover"],
            activeforeground=_COLORS["text"],
            relief=tk.FLAT,
            padx=16,
            pady=10,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            cursor="hand2",
            command=self.show_launcher,
        )
        self.menu_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.quit_btn = tk.Button(
            self.btn_row,
            text="Quit",
            font=_BTN_SECONDARY,
            bg=_COLORS["card_bg"],
            fg=_COLORS["muted"],
            activebackground=_COLORS["ghost_hover"],
            activeforeground=_COLORS["text"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            bd=0,
            highlightthickness=1,
            highlightbackground=_COLORS["ghost_border"],
            command=self.root.destroy,
        )
        self.quit_btn.pack(side=tk.LEFT)

    def _refresh_quiz_list(self) -> None:
        self.quiz_listbox.delete(0, tk.END)
        self._quiz_paths = list_quiz_paths(self.data_dir)
        for p in self._quiz_paths:
            try:
                t = read_quiz_title(p)
            except (OSError, ValueError, json.JSONDecodeError):
                t = p.stem
            self.quiz_listbox.insert(tk.END, f"{t}  —  {p.name}")

    def show_launcher(self) -> None:
        self.active_quiz_path = None
        self.play_panel.pack_forget()
        self.launcher_panel.pack(fill=tk.BOTH, expand=True)
        self.header.config(text="No-Brainers")
        self.header_tag.config(text="Pick a quiz or build your own")
        self._refresh_quiz_list()

    def _show_play(self) -> None:
        self.launcher_panel.pack_forget()
        self.play_panel.pack(fill=tk.BOTH, expand=True)

    def _launcher_start(self) -> None:
        sel = self.quiz_listbox.curselection()
        if not sel:
            messagebox.showinfo("Start quiz", "Select a quiz from the list first.")
            return
        path = self._quiz_paths[int(sel[0])]
        self.active_quiz_path = path
        self._show_play()
        self.start_new_quiz()

    def _open_create_dialog(self) -> None:
        CreateQuizDialog(self.root, self.data_dir, on_saved=self._after_quiz_saved)

    def _import_quiz(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        path_str = filedialog.askopenfilename(
            parent=self.root,
            title="Import quiz JSON",
            filetypes=[("Quiz JSON", "*.json"), ("All files", "*.*")],
        )
        if not path_str:
            return
        src = Path(path_str).resolve()
        try:
            validate_quiz_file(src)
        except (OSError, ValueError, json.JSONDecodeError, TypeError) as e:
            messagebox.showerror("Cannot import", str(e), parent=self.root)
            return

        dest = (self.data_dir / src.name).resolve()
        data_resolved = self.data_dir.resolve()

        if dest.exists():
            if not messagebox.askyesno(
                "Replace file?",
                f"A quiz named “{dest.name}” is already in your data folder.\nReplace it with the imported file?",
                parent=self.root,
            ):
                save_as = filedialog.asksaveasfilename(
                    parent=self.root,
                    title="Save imported quiz as",
                    initialdir=str(data_resolved),
                    initialfile=src.name,
                    defaultextension=".json",
                    filetypes=[("JSON", "*.json")],
                )
                if not save_as:
                    return
                dest = Path(save_as).resolve()
                if dest.parent.resolve() != data_resolved:
                    messagebox.showerror(
                        "Import",
                        "Save the file directly in the data folder (not a subfolder) so it shows in the list.",
                        parent=self.root,
                    )
                    return

        try:
            shutil.copy2(src, dest)
        except OSError as e:
            messagebox.showerror("Import failed", str(e), parent=self.root)
            return

        self._after_quiz_saved(dest)
        messagebox.showinfo("Imported", f"Quiz copied to:\n{dest.name}", parent=self.root)

    def _after_quiz_saved(self, path: Path) -> None:
        self._refresh_quiz_list()
        if path in self._quiz_paths:
            idx = self._quiz_paths.index(path)
            self.quiz_listbox.selection_clear(0, tk.END)
            self.quiz_listbox.selection_set(idx)
            self.quiz_listbox.see(idx)

    def start_new_quiz(self) -> None:
        if self.active_quiz_path is None:
            messagebox.showerror("No quiz", "No quiz file selected.")
            self.show_launcher()
            return
        try:
            data = load_quiz(self.active_quiz_path)
        except (OSError, ValueError, json.JSONDecodeError) as e:
            messagebox.showerror("Could not load quiz", str(e))
            self.show_launcher()
            return
        if not data.get("questions"):
            messagebox.showerror("Invalid quiz", "This quiz has no questions.")
            self.show_launcher()
            return

        self.quiz_title = data.get("title", "Quiz")
        self.questions = prepare_questions(data["questions"])
        self.index = 0
        self.score = 0
        self.awaiting_next = False

        self.header.config(text=self.quiz_title)
        self.header_tag.config(text="Test your knowledge · pick the best answer")
        self.summary_hint.config(text="")
        self.feedback.config(text="", fg=_COLORS["muted"], font=_FEEDBACK)
        self.main_btn.config(
            text="Submit",
            command=self._on_main_action,
            state="normal",
            bg=_COLORS["accent"],
            activebackground=_COLORS["accent_active"],
        )
        self.question_label.config(fg=_COLORS["text"], font=_BODY_STRONG)
        self._show_current_question()

    def _show_current_question(self) -> None:
        self.awaiting_next = False
        self.choice_var.set(-1)
        self.feedback.config(text="", fg=_COLORS["muted"], font=_FEEDBACK)
        self.summary_hint.config(text="")

        total = len(self.questions)
        self.progress.config(text=f"Question {self.index + 1} of {total}")

        pq = self.questions[self.index]
        self.question_label.config(text=pq.question)

        assert self.choices_frame is not None
        for w in self.choices_frame.winfo_children():
            w.destroy()

        for i, text in enumerate(pq.choices):
            row = tk.Frame(self.choices_frame, bg=_COLORS["card_bg"])
            row.pack(anchor="w", fill=tk.X, pady=4)

            rb = tk.Radiobutton(
                row,
                text=text,
                variable=self.choice_var,
                value=i,
                font=_CHOICE,
                anchor="w",
                bg=_COLORS["card_bg"],
                fg=_COLORS["text"],
                activebackground=_COLORS["card_bg"],
                activeforeground=_COLORS["text"],
                selectcolor="#e0f2fe",
                highlightthickness=0,
                padx=2,
                pady=6,
            )
            rb.pack(anchor="w", fill=tk.X)

        self._set_choice_widgets_state("normal")
        self.main_btn.config(text="Submit", state="normal")

    def _set_choice_widgets_state(self, state: str) -> None:
        assert self.choices_frame is not None
        for row in self.choices_frame.winfo_children():
            for w in row.winfo_children():
                w.config(state=state)

    def _on_main_action(self) -> None:
        if not self.awaiting_next:
            self._submit_answer()
        else:
            self._go_next()

    def _submit_answer(self) -> None:
        sel = self.choice_var.get()
        if sel < 0:
            messagebox.showwarning("No answer", "Please select an answer.")
            return

        pq = self.questions[self.index]
        correct = sel == pq.correct_index
        if correct:
            self.score += 1
            self.feedback.config(text="Nice — that's correct.", fg=_COLORS["success"], font=_FEEDBACK)
        else:
            right = pq.choices[pq.correct_index]
            self.feedback.config(
                text=f"Not quite. The correct answer was: {right}",
                fg=_COLORS["error"],
                font=_FEEDBACK,
            )

        self._set_choice_widgets_state("disabled")
        self.awaiting_next = True
        self.main_btn.config(text="Next question")

    def _go_next(self) -> None:
        self.index += 1
        if self.index >= len(self.questions):
            self._show_summary()
            return
        self._show_current_question()

    def _show_summary(self) -> None:
        total = len(self.questions)
        self.progress.config(text="All done")
        self.question_label.config(text="Here's how you did", font=_BODY_STRONG, fg=_COLORS["text"])
        assert self.choices_frame is not None
        for w in self.choices_frame.winfo_children():
            w.destroy()

        pct = round(100 * self.score / total) if total else 0
        self.feedback.config(
            text=f"{self.score} / {total}",
            fg=_COLORS["accent"],
            font=_SCORE,
        )
        self.summary_hint.config(text=f"{pct}% correct · Play again to reshuffle questions")

        self.main_btn.config(
            text="Play again",
            command=self.start_new_quiz,
            bg=_COLORS["accent"],
            activebackground=_COLORS["accent_active"],
        )

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    QuizApp().run()


if __name__ == "__main__":
    main()
