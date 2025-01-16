import tkinter as tk
from tkinter import ttk, messagebox
import requests
import random

class TriviaAPI:
    BASE_URL = "https://opentdb.com/api.php?amount=10"

    def __init__(self, num_questions=10, category=None, difficulty=None):
        self.num_questions = num_questions
        self.category = category
        self.difficulty = difficulty

    def fetch_questions(self):
        params = {
            "amount": self.num_questions,
            "type": "multiple",
            "difficulty": self.difficulty
        }
        if self.category:
            params["category"] = self.category

        response = requests.get(self.BASE_URL, params=params)
        data = response.json()
        if data["response_code"] == 0:
            return data["results"]
        else:
            messagebox.showerror("Error", "Failed to retrieve questions")
            return []

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Open Trivia Quiz")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f4f8")  

        self.score = 0
        self.current_question = 0
        self.questions = []
        self.timer = None

        self.setup_styles()
        self.setup_gui()

    def setup_styles(self):
        """Define styles for buttons and widgets."""
        style = ttk.Style()

        style.configure("Start.TButton",
                        font=("Helvetica", 14),
                        background="#4CAF50",  
                        foreground="white",
                        padding=10,
                        relief="flat")
        style.map("Start.TButton",
                  background=[("active", "#388E3C")])  

        style.configure("Answer.TButton",
                        font=("Helvetica", 12),
                        background="#E0E0E0",  
                        foreground="#333333",  
                        padding=10,
                        relief="flat")
        style.map("Answer.TButton",
                  background=[("active", "#90CAF9")],  
                  foreground=[("active", "#000000")])  

        style.configure("TLabel", 
                        font=("Helvetica", 14), 
                        background="#f0f4f8", 
                        foreground="#333333")

    def setup_gui(self):
        self.selection_frame = ttk.Frame(self.root, padding=20, style="TFrame")
        self.selection_frame.pack(pady=50)

        ttk.Label(self.selection_frame, text="Select Category:").grid(row=0, column=0)
        self.category_var = tk.StringVar()
        categories = {"General Knowledge": 9, "Science & Nature": 17, "Sports": 21}
        self.category_dropdown = ttk.Combobox(self.selection_frame, textvariable=self.category_var, 
                                              values=list(categories.keys()), state="readonly")
        self.category_dropdown.grid(row=0, column=1, padx=10)
        self.category_dropdown.set("General Knowledge")

        ttk.Label(self.selection_frame, text="Select Difficulty:").grid(row=1, column=0, pady=10)
        self.difficulty_var = tk.StringVar()
        self.difficulty_dropdown = ttk.Combobox(self.selection_frame, textvariable=self.difficulty_var, 
                                                values=["easy", "medium", "hard"], state="readonly")
        self.difficulty_dropdown.grid(row=1, column=1, padx=10)
        self.difficulty_dropdown.set("medium")

        self.start_button = ttk.Button(self.selection_frame, text="Start Quiz", 
                                       command=lambda: self.start_quiz(categories), style="Start.TButton")
        self.start_button.grid(row=2, column=0, columnspan=2, pady=20)

    def start_quiz(self, categories):
        category_name = self.category_var.get()
        category_id = categories.get(category_name)
        difficulty = self.difficulty_var.get()
        self.questions = TriviaAPI(category=category_id, difficulty=difficulty).fetch_questions()

        if self.questions:
            self.score = 0
            self.current_question = 0
            self.display_question()
        else:
            messagebox.showerror("Error", "No questions available.")

    def display_question(self):
        if self.timer:
            self.root.after_cancel(self.timer)

        question_data = self.questions[self.current_question]
        question_text = question_data["question"]
        correct_answer = question_data["correct_answer"]
        incorrect_answers = question_data["incorrect_answers"]

        options = incorrect_answers + [correct_answer]
        random.shuffle(options)

        for widget in self.root.winfo_children():
            widget.destroy()

        progress = f"Question {self.current_question + 1}/{len(self.questions)}"
        ttk.Label(self.root, text=progress, font=("Helvetica", 16)).pack(pady=10)

        ttk.Label(self.root, text=question_text, font=("Helvetica", 18), wraplength=600).pack(pady=20)

        for option in options:
            ttk.Button(self.root, text=option, 
                       command=lambda opt=option: self.check_answer(opt, correct_answer), 
                       style="Answer.TButton").pack(pady=5)

        self.time_remaining = 20
        self.timer_label = ttk.Label(self.root, text=f"Time Remaining: {self.time_remaining}s", 
                                     font=("Helvetica", 14), foreground="#D32F2F")
        self.timer_label.pack(pady=10)
        self.update_timer()

    def update_timer(self):
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.config(text=f"Time Remaining: {self.time_remaining}s")
            self.timer = self.root.after(1000, self.update_timer)
        else:
            self.check_answer(None, correct_answer=None)  
    def check_answer(self, selected, correct):
        if selected == correct:
            self.score += 1

        self.current_question += 1
        if self.current_question < len(self.questions):
            self.display_question()
        else:
            self.show_results()

    def show_results(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Quiz Complete!", font=("Helvetica", 24)).pack(pady=30)
        ttk.Label(self.root, text=f"Your Score: {self.score}/{len(self.questions)}", font=("Helvetica", 18)).pack(pady=20)

        restart_button = ttk.Button(self.root, text="Restart Quiz", command=self.setup_gui, style="Start.TButton")
        restart_button.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
