import customtkinter as ctk

from frontend.login_view import LoginView
from frontend.quiz_view import QuizView

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


def main():
    root = ctk.CTk()
    root.title("No Brainers")
    root.geometry("950x620")

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
