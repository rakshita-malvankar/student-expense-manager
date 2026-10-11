import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from collections import defaultdict
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    CHART_AVAILABLE = True
except ImportError:
    CHART_AVAILABLE = False
# ---------------- COLORS ----------------
BG = "#F5F3FF"
BLUE = "#6C5CE7"
DARK_BLUE = "#5746D8"
TEXT = "#2D3436"
WHITE = "#FFFFFF"
LIGHT_BLUE = "#EDE9FE"
BORDER = "#DDD6FE"
# ---------------- DATABASE ----------------
def create_database():
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in cursor.fetchall()]
    if "date" not in columns:
        cursor.execute(
            "ALTER TABLE expenses ADD COLUMN date TEXT"
        )
    connection.commit()
    connection.close()
# ---------------- APP ----------------
app = tk.Tk()
app.title("Student Expense Manager")
app.geometry("1000x700")
app.configure(bg="#F4F7FC")
app.minsize(850, 600)
# ---------------- SCROLLABLE AREA ----------------
main_canvas = tk.Canvas(
    app,
    bg=BG,
    highlightthickness=0
)
main_canvas.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)
main_scrollbar = tk.Scrollbar(
    app,
    orient=tk.VERTICAL,
    command=main_canvas.yview
)
main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
main_canvas.configure(
    yscrollcommand=main_scrollbar.set
)
main_frame = tk.Frame(main_canvas, bg=BG)
canvas_window = main_canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)
def resize_main_frame(event):
    main_canvas.itemconfig(
        canvas_window,
        width=event.width
    )
main_canvas.bind("<Configure>", resize_main_frame)
def update_scroll_area(event=None):
    main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )
main_frame.bind("<Configure>", update_scroll_area)
# ---------------- VARIABLES ----------------
expenses = []
displayed_expenses = []
budget = 0.0
# ---------------- TITLE ----------------
title = tk.Label(
    main_frame,
    text="Student Expense Manager",
    font=("Arial", 26, "bold"),
    bg=BG,
    fg=BLUE
)
title.pack(pady=(12, 4))
subtitle = tk.Label(
    main_frame,
    text="Track your spending. Manage your money smarter",
    font=("Arial", 12),
    bg=BG,
    fg=TEXT
)
subtitle.pack(pady=(0, 10))
# ---------------- BUDGET ----------------
budget_frame = tk.Frame(main_frame, bg=BG)
budget_frame.pack(pady=10)
tk.Label(
    budget_frame,
    text="Monthly Budget:",
    font=("Arial", 11, "bold"),
    bg=BG,
    fg=TEXT
).grid(row=0, column=0, padx=5, pady=5)
budget_entry = tk.Entry(
    budget_frame,
    width=20,
    font=("Arial", 11)
)
budget_entry.grid(row=0, column=1, padx=5, pady=5)
# ---------------- INPUT AREA ----------------
tk.Label(
    main_frame,
    text="Add a New Expense",
    font=("Arial", 16, "bold"),
    bg=BG,
    fg=BLUE
    ).pack(pady=(10, 0))
input_frame = tk.Frame(
    main_frame,
    bg=WHITE,
    padx=30,
    pady=22,
    highlightbackground=BORDER,
    highlightthickness=1
)
input_frame.pack(pady=15)
def create_field_label(text, row):
    tk.Label(
        input_frame,
        text=text,
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=TEXT
    ).grid(
        row=row,
        column=0,
        padx=12,
        pady=10,
        sticky="w"
    )
def create_entry(row):
    entry = tk.Entry(
        input_frame,
        width=32,
        font=("Arial", 11),
        bg="#FAFAFF",
        fg=TEXT,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=BLUE,
        insertbackground=TEXT
    )
    entry.grid(
        row=row,
        column=1,
        padx=12,
        pady=10,
        ipady=7
    )
    return entry
create_field_label("Expense Name:", 0)
name_entry = create_entry(0)
create_field_label("Amount (₹):", 1)
amount_entry = create_entry(1)
create_field_label("Category:", 2)
category_entry = create_entry(2)
create_field_label("Date:", 3)
date_entry = create_entry(3)
# ---------------- TOTAL ----------------
# ---------------- DASHBOARD CARDS ----------------
dashboard_frame = tk.Frame(main_frame, bg=BG)
dashboard_frame.pack(fill=tk.X, padx=15, pady=10)

for column in range(3):
    dashboard_frame.grid_columnconfigure(column, weight=1)

# Total Expenses Card
total_card = tk.Frame(
    dashboard_frame,
    bg=WHITE,
    padx=12,
    pady=22,
    highlightbackground=BORDER,
    highlightthickness=1
)
total_card.grid(row=0, column=0, padx=7, sticky="nsew")

tk.Label(
    total_card,
    text="TOTAL EXPENSES",
    font=("Arial", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).pack(pady=(0, 8))

total_label = tk.Label(
    total_card,
    text="₹0.00",
    font=("Arial", 17, "bold"),
    bg=WHITE,
    fg=BLUE
)
total_label.pack()

# Monthly Budget Card
budget_card = tk.Frame(
    dashboard_frame,
    bg=WHITE,
    padx=12,
    pady=22,
    highlightbackground=BORDER,
    highlightthickness=1
)
budget_card.grid(row=0, column=1, padx=7, sticky="nsew")

tk.Label(
    budget_card,
    text="MONTHLY BUDGET",
    font=("Arial", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).pack(pady=(0, 8))

budget_label = tk.Label(
    budget_card,
    text="₹0.00",
    font=("Arial", 17, "bold"),
    bg=WHITE,
    fg=BLUE
)
budget_label.pack()

# Remaining Budget Card
remaining_card = tk.Frame(
    dashboard_frame,
    bg=WHITE,
    padx=12,
    pady=22,
    highlightbackground=BORDER,
    highlightthickness=1
)
remaining_card.grid(row=0, column=2, padx=7, sticky="nsew")

tk.Label(
    remaining_card,
    text="REMAINING BUDGET",
    font=("Arial", 10, "bold"),
    bg=WHITE,
    fg=TEXT
).pack(pady=(0, 8))

remaining_label = tk.Label(
    remaining_card,
    text="₹0.00",
    font=("Arial", 17, "bold"),
    bg=WHITE,
    fg=TEXT
)
remaining_label.pack()

#----------------- EXPENSE CHART ----------------
chart_frame=tk.Frame(
    main_frame,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1
)
chart_frame.pack(fill=tk.X, padx=20, pady=15)
chart_title = tk.Label(
    chart_frame,
    text="Expenses by Category",
    font=("Arial", 15, "bold"),
    bg=WHITE,
    fg=BLUE
)
chart_title.pack(anchor="w", padx=20, pady=15)
# ---------------- DRAW EXPENSE CHART ---------------
chart_area = tk.Frame(chart_frame, bg=WHITE)
chart_area.pack(fill=tk.X, padx=10, pady=10)
if CHART_AVAILABLE:
    figure = Figure(figsize=(6, 3.5), dpi=100,facecolor=WHITE)
    ax = figure.add_subplot(111)
    chart_canvas = FigureCanvasTkAgg(
        figure, master=chart_area
    )
    chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    def draw_expense_chart():
        ax.clear()
        ax.set_facecolor(WHITE)
        category_totals = {}

        for expense in expenses:
            category = expense["category"] or "Other"
            old_total = category_totals.get(category, 0)
            category_totals[category] = old_total + expense["amount"]

        if category_totals:
            ax.pie(
                list(category_totals.values()),
                labels=list(category_totals.keys()),
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 9}
            )
            ax.set_title(
                "Expenses by Category",
                fontsize=13,
                fontweight="bold",
                color=TEXT,
                pad=15
            )
            ax.axis("equal")
        else:
            ax.text(
                0.5, 0.5,
                "No expenses to display",
                ha="center",
                va="center",
                transform=ax.transAxes
            )
            ax.set_title("Expenses by Category")

        figure.tight_layout()
        chart_canvas.draw()
else:
    tk.Label(
        chart_area,
        text="Insall matplotlib to display the chartactivebackground=",
        bg=WHITE,
        fg=TEXT
    ).pack()
# ---------------- EXPENSE LIST ----------------
tk.Label(
    main_frame,
    text="Your Expenses",
    font=("Arial", 18, "bold"),
    bg=BG,
    fg=BLUE
).pack(pady=(22, 10))
expense_list_frame = tk.Frame(main_frame, bg=BG)
expense_list_frame.pack(pady=12, padx=20)
expense_list = tk.Listbox(
    expense_list_frame,
    width=85,
    height=12,
    font=("Arial", 11),
    bg=WHITE,
    fg=TEXT,
    selectbackground=BLUE,
    selectforeground=WHITE,
    relief="flat",
    bd=0,
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=BLUE,
    activestyle="none"
)
expense_list.pack(side=tk.LEFT, fill=tk.BOTH)
expense_scrollbar = tk.Scrollbar(
    expense_list_frame,
    orient=tk.VERTICAL,
    command=expense_list.yview
)
expense_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
expense_list.config(
    yscrollcommand=expense_scrollbar.set
)
# ---------------- UPDATE TOTAL ----------------
def update_total():
    total = sum(expense["amount"] for expense in expenses)
    total_label.config(
        text=f"₹{total:.2f}"
    )
    update_remaining_budget()
# ---------------- REMAINING BUDGET ----------------
def update_remaining_budget():
    total = sum(expense["amount"] for expense in expenses)
    remaining = budget - total
    remaining_label.config(
        text=f"₹{remaining:.2f}",
        fg="#DC2626" if remaining < 0 else "#16A34A"
    )
    if remaining < 0:
        remaining_label.config(fg="#DC2626")
    else:
        remaining_label.config(fg=TEXT)
# ---------------- BUDGET BUTTON ----------------
def set_budget():
    global budget
    budget_text = budget_entry.get().strip()
    try:
        new_budget = float(budget_text)
        if new_budget < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Budget",
            "Please enter a valid non-negative budget."
        )
        return
    budget = new_budget
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        ("monthly_budget", str(budget))
    )
    connection.commit()
    connection.close()
    budget_label.config(text=f"₹{budget:.2f}")
    update_remaining_budget()
    budget_entry.delete(0, tk.END)
budget_button = tk.Button(
    budget_frame,
    text="Set Budget",
    command=set_budget,
    width=12,
    bg=BLUE,
    fg=WHITE,
    activebackground=DARK_BLUE,
    activeforeground=WHITE,
    font=("Arial", 10, "bold"),
    relief="flat",
    borderwidth=0,
    cursor="hand2",
    padx=8,
    pady=6
)
budget_button.grid(row=0, column=2, padx=5, pady=5)
# ---------------- SHOW EXPENSES ----------------
def show_all_expenses():
    global displayed_expenses
    displayed_expenses = list(expenses)
    expense_list.delete(0, tk.END)
    for expense in displayed_expenses:
        expense_list.insert(
            tk.END,
            f'{expense["name"]}  |  ₹{expense["amount"]:.2f}  |  '
            f'{expense["category"]}  |  {expense["date"]}'
        )
# ---------------- LOAD EXPENSES ----------------
def load_expenses():
    expenses.clear()
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT value FROM settings WHERE key = ?",
        ("monthly_budget",)
    )
    result = cursor.fetchone()
    global budget
    if result is not None:
        budget = float(result[0])
    else:
        budget=0
    budget_label.config(text=f"₹{budget:.2f}")
    cursor.execute(
        "SELECT id, name, amount, category, date FROM expenses"
    )
    rows = cursor.fetchall()
    connection.close()
    for row in rows:
        expense_id, name, amount, category, date = row
        expenses.append({
            "id": expense_id,
            "name": name or "",
            "amount": float(amount or 0),
            "category": category or "",
            "date": date or ""
        })
    show_all_expenses()
    update_total()
    if CHART_AVAILABLE:
        draw_expense_chart()
# ---------------- ADD EXPENSE ----------------
def add_expense():
    name = name_entry.get().strip()
    amount_text = amount_entry.get().strip()
    category = category_entry.get().strip()
    date = date_entry.get().strip()
    if not name or not amount_text or not category or not date:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all four fields."
        )
        return
    try:
        amount = float(amount_text)
        if amount < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid non-negative number."
        )
        return
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO expenses (name, amount, category, date)
        VALUES (?, ?, ?, ?)
        """,
        (name, amount, category, date)
    )
    expense_id = cursor.lastrowid
    connection.commit()
    connection.close()
    expenses.append({
        "id": expense_id,
        "name": name,
        "amount": amount,
        "category": category,
        "date": date
    })
    show_all_expenses()
    update_total()
    if CHART_AVAILABLE:
        draw_expense_chart()
    clear_fields()
def clear_fields():
    name_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
def styled_button(parent, text, command, color=BLUE, width=18):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=color,
        fg=WHITE if color != "#E2E8F0" else TEXT,
        activebackground=DARK_BLUE if color == BLUE else color,
        activeforeground=WHITE if color != "#E2E8F0" else TEXT,
        font=("Arial", 10, "bold"),
        relief="flat",
        cursor="hand2",
        padx=8,
        pady=8
    )
add_button = styled_button(
    main_frame,
    "Add Expense",
    add_expense,
    BLUE,
    22
)
add_button.pack(pady=8)
# ---------------- SEARCH ----------------
search_frame = tk.Frame(main_frame, bg=BG)
search_frame.pack(pady=18)
tk.Label(
    search_frame,
    text="Search Expenses:",
    bg=BG,
    fg=TEXT,
    font=("Arial", 11, "bold")
).grid(row=0, column=0, padx=8)
search_entry = tk.Entry(
    search_frame,
    width=32,
    font=("Arial", 11),
    bg=WHITE,
    fg=TEXT,
    relief="flat",
    bd=0,
    highlightthickness=1,
    highlightbackground=BORDER,
    highlightcolor=BLUE,
    insertbackground=TEXT
)
search_entry.grid(
    row=0,
    column=1,
    padx=8,
    ipady=6
)
def search_expenses():
    global displayed_expenses
    search_text = search_entry.get().strip().lower()
    displayed_expenses = [
        expense for expense in expenses
        if search_text in expense["name"].lower()
        or search_text in expense["category"].lower()
    ]
    expense_list.delete(0, tk.END)
    for expense in displayed_expenses:
        expense_list.insert(
            tk.END,
            f'{expense["name"]}  |  ₹{expense["amount"]:.2f}  |  '
            f'{expense["category"]}  |  {expense["date"]}'
        )
search_button = styled_button(
    search_frame,
    "Search",
    search_expenses,
    BLUE,
    10
)
search_button.grid(row=0, column=2, padx=5, ipady=4)
show_all_button = styled_button(
    search_frame,
    "Show All",
    show_all_expenses,
    "#E2E8F0",
    10
)
show_all_button.grid(row=0, column=3, padx=5, ipady=4)
# ---------------- SELECT EXPENSE ----------------
def get_selected_expense():
    selected = expense_list.curselection()
    if not selected:
        messagebox.showwarning(
            "No Selection",
            "Please select an expense from the list."
        )
        return None
    return displayed_expenses[selected[0]]
def fill_fields_from_selection(event=None):
    selected = expense_list.curselection()
    if not selected:
        return
    expense = displayed_expenses[selected[0]]
    clear_fields()
    name_entry.insert(0, expense["name"])
    amount_entry.insert(0, str(expense["amount"]))
    category_entry.insert(0, expense["category"])
    date_entry.insert(0, expense["date"])
expense_list.bind("<<ListboxSelect>>", fill_fields_from_selection)
# ---------------- EDIT SELECTED EXPENSE ----------------
def edit_expense():
    expense = get_selected_expense()
    if expense is None:
        return
    name = simpledialog.askstring(
        "Edit Expense",
        "Enter expense name:",
        initialvalue=expense["name"],
        parent=app
    )
    if name is None:
        return
    amount_text = simpledialog.askstring(
        "Edit Expense",
        "Enter amount:",
        initialvalue=str(expense["amount"]),
        parent=app
    )
    if amount_text is None:
        return
    category = simpledialog.askstring(
        "Edit Expense",
        "Enter category:",
        initialvalue=expense["category"],
        parent=app
    )
    if category is None:
        return
    date = simpledialog.askstring(
        "Edit Expense",
        "Enter date:",
        initialvalue=expense["date"],
        parent=app
    )
    if date is None:
        return
    name = name.strip()
    category = category.strip()
    date = date.strip()
    if not name or not category or not date:
        messagebox.showwarning(
            "Missing Information",
            "Fields cannot be empty."
        )
        return
    try:
        amount = float(amount_text)
        if amount < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid non-negative amount."
        )
        return
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE expenses
        SET name = ?, amount = ?, category = ?, date = ?
        WHERE id = ?
        """,
        (name, amount, category, date, expense["id"])
    )
    connection.commit()
    connection.close()
    expense["name"] = name
    expense["amount"] = amount
    expense["category"] = category
    expense["date"] = date
    show_all_expenses()
    update_total()
    if CHART_AVAILABLE:
        draw_expense_chart()
    messagebox.showinfo(
        "Success",
        "Expense updated successfully!"
    )
# ---------------- SAVE CHANGES FROM FIELDS ----------------
def save_changes():
    expense = get_selected_expense()
    if expense is None:
        return
    name = name_entry.get().strip()
    amount_text = amount_entry.get().strip()
    category = category_entry.get().strip()
    date = date_entry.get().strip()
    if not name or not amount_text or not category or not date:
        messagebox.showwarning(
            "Missing Information",
            "Please fill in all four fields."
        )
        return
    try:
        amount = float(amount_text)
        if amount < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid non-negative amount."
        )
        return
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE expenses
        SET name = ?, amount = ?, category = ?, date = ?
        WHERE id = ?
        """,
        (name, amount, category, date, expense["id"])
    )
    connection.commit()
    connection.close()
    expense["name"] = name
    expense["amount"] = amount
    expense["category"] = category
    expense["date"] = date
    show_all_expenses()
    update_total()
    clear_fields()
    messagebox.showinfo(
        "Success",
        "Expense updated successfully!"
    )
# ---------------- EDIT / SAVE BUTTONS ----------------
edit_button = styled_button(
    main_frame,
    "Edit Selected Expense",
    edit_expense,
    BLUE,
    25
)
edit_button.pack(pady=5)
save_button = styled_button(
    main_frame,
    "Save Changes from Fields",
    save_changes,
    BLUE,
    25
)
save_button.pack(pady=5)
clear_button = styled_button(
    main_frame,
    "Clear Input Fields",
    clear_fields,
    "#E2E8F0",
    25
)
clear_button.pack(pady=5)
# ---------------- DELETE EXPENSE ----------------
def delete_expense():
    expense = get_selected_expense()
    if expense is None:
        return
    confirm = messagebox.askyesno(
        "Confirm Delete",
        f'Delete "{expense["name"]}"?'
    )
    if not confirm:
        return
    connection = sqlite3.connect("expenses.db")
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense["id"],)
    )
    connection.commit()
    connection.close()
    expenses.remove(expense)
    show_all_expenses()
    update_total()
    if CHART_AVAILABLE:
        draw_expense_chart()
    clear_fields()
delete_button = styled_button(
    main_frame,
    "Delete Selected Expense",
    delete_expense,
    "#DC2626",
    25
)
delete_button.pack(pady=5)
# ---------------- CATEGORY SUMMARY ----------------
def show_summary():
    category_totals = {}
    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]
        category_totals[category] = (
            category_totals.get(category, 0) + amount
        )
    if not category_totals:
        summary_text = "No expenses to summarize yet."
    else:
        summary_text = "Category Summary\n\n"
        for category, amount in sorted(category_totals.items()):
            summary_text += f"{category}: ₹{amount:.2f}\n"
    summary_label.config(text=summary_text)
summary_button = styled_button(
    main_frame,
    "Show Category Summary",
    show_summary,
    BLUE,
    25
)
summary_button.pack(pady=10)
summary_label = tk.Label(
    main_frame,
    text="",
    font=("Arial", 12),
    bg=BG,
    fg=TEXT,
    justify="left"
)
summary_label.pack(pady=10)
# ---------------- START DATABASE ----------------
create_database()
load_expenses()
app.mainloop()
