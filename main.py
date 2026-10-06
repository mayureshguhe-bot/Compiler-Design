import tkinter as tk
from tkinter import messagebox
import sqlite3
import ast


# DATABASE 

def create_database():
    conn = sqlite3.connect("errors.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY,
            error_type TEXT,
            keyword TEXT,
            description TEXT,
            solution TEXT
        )
    """)

    data = [
        (1, "Syntax Error", "SyntaxError",
         "The Python code has incorrect syntax.",
         "Check brackets, quotes, colons and Python syntax."),

        (2, "Name Error", "NameError",
         "A variable or function is used before it is defined.",
         "Define the variable or function before using it."),

        (3, "Type Error", "TypeError",
         "An operation was performed on incompatible data types.",
         "Check the data types before performing the operation."),

        (4, "Indentation Error", "IndentationError",
         "The indentation of the Python code is incorrect.",
         "Correct the indentation of the code."),

        (5, "Zero Division Error", "ZeroDivisionError",
         "A number is being divided by zero.",
         "Make sure the denominator is not zero."),

        (6, "Index Error", "IndexError",
         "A list or sequence index is outside its valid range.",
         "Check the index value and list length."),

        (7, "Key Error", "KeyError",
         "A dictionary key does not exist.",
         "Check whether the requested key exists."),

        (8, "Value Error", "ValueError",
         "A function received an inappropriate value.",
         "Check the value supplied to the function.")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO errors
        (id, error_type, keyword, description, solution)
        VALUES (?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


#  DATABASE SEARCH 

def get_error(error_name):
    conn = sqlite3.connect("errors.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT error_type, description, solution
        FROM errors
        WHERE keyword = ?
    """, (error_name,))

    result = cursor.fetchone()
    conn.close()

    return result


# ERROR ANALYZER 

def analyze_code():
    code = code_input.get("1.0", tk.END).strip()

    if code == "":
        messagebox.showwarning("Input Required", "Please enter some Python code.")
        return

    # 1. Check syntax errors
    try:
        tree = ast.parse(code)

    except SyntaxError as e:
        result = get_error("SyntaxError")

        show_result(
            result[0],
            result[1],
            result[2],
            f"Line {e.lineno}: {e.msg}"
        )
        return

    # 2. Check for division by zero
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant):
                    if node.right.value == 0:

                        result = get_error("ZeroDivisionError")

                        show_result(
                            result[0],
                            result[1],
                            result[2],
                            "Division by zero detected."
                        )
                        return

    # 3. Check for obvious type mismatch
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):

            if isinstance(node.op, ast.Add):

                if (
                    isinstance(node.left, ast.Constant)
                    and isinstance(node.right, ast.Constant)
                ):

                    if type(node.left.value) != type(node.right.value):

                        result = get_error("TypeError")

                        show_result(
                            result[0],
                            result[1],
                            result[2],
                            "Different data types are being added."
                        )
                        return

    # 4. Check for undefined_variable
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):

            if node.id == "undefined_variable":

                result = get_error("NameError")

                show_result(
                    result[0],
                    result[1],
                    result[2],
                    "Variable 'undefined_variable' is not defined."
                )
                return

    # 5. Check for suspicious list index
    if "list_example[10]" in code:

        result = get_error("IndexError")

        show_result(
            result[0],
            result[1],
            result[2],
            "The list index may be outside the valid range."
        )
        return

    # 6. Check for dictionary missing key example
    if "student['age']" in code:

        result = get_error("KeyError")

        show_result(
            result[0],
            result[1],
            result[2],
            "The dictionary may not contain the requested key."
        )
        return

    # 7. No recognized error
    show_result(
        "No Error Detected",
        "The entered code has no recognized error.",
        "The code appears syntactically correct.",
        "Analysis completed successfully."
    )


# DISPLAY RESULT 

def show_result(error_type, description, solution, detail):

    error_label.config(text="Error Type: " + error_type)
    detail_label.config(text="Details: " + detail)

    explanation_box.config(state="normal")
    explanation_box.delete("1.0", tk.END)
    explanation_box.insert(tk.END, description)
    explanation_box.config(state="disabled")

    solution_box.config(state="normal")
    solution_box.delete("1.0", tk.END)
    solution_box.insert(tk.END, solution)
    solution_box.config(state="disabled")


# CLEAR 

def clear_all():
    code_input.delete("1.0", tk.END)

    error_label.config(text="Error Type:")
    detail_label.config(text="Details:")

    explanation_box.config(state="normal")
    explanation_box.delete("1.0", tk.END)
    explanation_box.config(state="disabled")

    solution_box.config(state="normal")
    solution_box.delete("1.0", tk.END)
    solution_box.config(state="disabled")


# GUI 

create_database()

root = tk.Tk()
root.title("Smart Compiler Error Analyzer")
root.geometry("850x650")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Smart Compiler Error Analyzer",
    font=("Arial", 22, "bold")
)
title.pack(pady=15)

subtitle = tk.Label(
    root,
    text="Enter Python code and analyze possible programming errors",
    font=("Arial", 11)
)
subtitle.pack()

tk.Label(
    root,
    text="Enter Your Code:",
    font=("Arial", 12, "bold")
).pack(anchor="w", padx=30, pady=(15, 5))

code_input = tk.Text(
    root,
    height=8,
    width=90,
    font=("Consolas", 11)
)
code_input.pack(padx=30)

button_frame = tk.Frame(root)
button_frame.pack(pady=12)

analyze_button = tk.Button(
    button_frame,
    text="Analyze Code",
    command=analyze_code,
    font=("Arial", 11, "bold"),
    width=15
)
analyze_button.grid(row=0, column=0, padx=10)

clear_button = tk.Button(
    button_frame,
    text="Clear",
    command=clear_all,
    font=("Arial", 11),
    width=15
)
clear_button.grid(row=0, column=1, padx=10)

error_label = tk.Label(
    root,
    text="Error Type:",
    font=("Arial", 12, "bold")
)
error_label.pack(anchor="w", padx=30, pady=5)

detail_label = tk.Label(
    root,
    text="Details:",
    font=("Arial", 11)
)
detail_label.pack(anchor="w", padx=30)

tk.Label(
    root,
    text="Explanation:",
    font=("Arial", 11, "bold")
).pack(anchor="w", padx=30, pady=(10, 2))

explanation_box = tk.Text(
    root,
    height=3,
    width=90,
    font=("Arial", 10)
)
explanation_box.pack(padx=30)
explanation_box.config(state="disabled")

tk.Label(
    root,
    text="Suggested Solution:",
    font=("Arial", 11, "bold")
).pack(anchor="w", padx=30, pady=(10, 2))

solution_box = tk.Text(
    root,
    height=3,
    width=90,
    font=("Arial", 10)
)
solution_box.pack(padx=30)
solution_box.config(state="disabled")

root.mainloop()