import customtkinter as ctk
import tkinter as tk
import random
import math

class SpinWheel(ctk.CTkFrame):
    def __init__(self, parent, options):
        super().__init__(parent)

        self.options = options
        self.angle = 0

        self.canvas = tk.Canvas(self, width=300, height=300, bg="white")
        self.canvas.pack(pady=20)

        self.result_label = ctk.CTkLabel(self, text="Click spin!")
        self.result_label.pack(pady=10)

        self.spin_button = ctk.CTkButton(self, text="Spin", command=self.spin)
        self.spin_button.pack(pady=10)

        self.draw_wheel()

    def draw_wheel(self):
        self.canvas.delete("all")

        num_options = len(self.options)
        slice_angle = 360 / num_options

        for i, option in enumerate(self.options):
            start_angle = self.angle + i * slice_angle
            self.canvas.create_arc(
                20, 20, 280, 280,
                start=start_angle,
                extent=slice_angle,
                fill=f"#{random.randint(100,255):02x}{random.randint(100,255):02x}{random.randint(100,255):02x}",
                outline="black"
            )

            text_angle = math.radians(start_angle + slice_angle / 2)
            x = 150 + 80 * math.cos(text_angle)
            y = 150 - 80 * math.sin(text_angle)

            self.canvas.create_text(x, y, text=option, font=("Arial", 12, "bold"))

        self.canvas.create_polygon(140, 5, 160, 5, 150, 30, fill="red")

    def spin(self):
        spins = random.randint(30, 50)

        def animate(count):
            if count > 0:
                self.angle += random.randint(10, 25)
                self.draw_wheel()
                self.after(50, animate, count - 1)
            else:
                winner = random.choice(self.options)
                self.result_label.configure(text=f"Winner: {winner}")

        animate(spins)


app = ctk.CTk()
app.geometry("400x450")
app.title("Spin Wheel")

wheel = SpinWheel(app, ["Math", "Science", "History", "Python"])
wheel.pack(pady=20)

app.mainloop()