import csv
import os
import sys

# Safely reconfigure stdout to avoid UnicodeEncodeError on Windows terminals when printing emojis/rupee symbols
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

# This is the file where all expenses will be saved
FILE_NAME = "expenses.csv"


# ------------------------------------------------
# Function to add a new expense
# ------------------------------------------------
def add_expense():
    print("\n--- Add New Expense ---")
    description = input("Enter expense description (e.g. Coffee, Rent): ").strip()
    
    # Keep asking until user gives a valid number
    while True:
        amount = input("Enter amount (in ₹): ").strip()
        try:
            amount_val = float(amount)
            if amount_val < 0:
                print("Amount cannot be negative! Please enter a positive number.")
                continue
            amount = amount_val
            break
        except ValueError:
            print("Invalid amount! Please enter a number.")

    # Open the CSV file in append mode and write the new row (using UTF-8 encoding)
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([description, amount])

    print(f"✅ Expense '{description}' of ₹{amount:.2f} added successfully!")


# ------------------------------------------------
# Function to view all saved expenses
# ------------------------------------------------
def view_expenses():
    print("\n--- All Expenses ---")

    # Check if the file exists and has any data
    if not os.path.exists(FILE_NAME):
        print("No expenses found. Please add some expenses first.")
        return

    expenses = []

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # skip empty rows just in case
                expenses.append(row)

    if len(expenses) == 0:
        print("No expenses found. Please add some expenses first.")
        return

    # Print a simple table header
    print(f"\n{'No.':<5} {'Description':<25} {'Amount (₹)':>12}")
    print("-" * 45)

    for i, row in enumerate(expenses, start=1):
        try:
            desc = row[0]
            # Truncate long descriptions to maintain table alignment
            if len(desc) > 25:
                desc = desc[:22] + "..."
            amount = float(row[1])
            print(f"{i:<5} {desc:<25} {amount:>12.2f}")
        except (IndexError, ValueError):
            print(f"{i:<5} [Corrupted Row]           {'N/A':>12}")

    print("-" * 45)


# ------------------------------------------------
# Function to show total amount spent
# ------------------------------------------------
def total_expenses():
    print("\n--- Total Expenses ---")

    if not os.path.exists(FILE_NAME):
        print("No expenses found. Please add some expenses first.")
        return

    total = 0.0
    count = 0
    corrupted_count = 0

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                try:
                    total += float(row[1])
                    count += 1
                except (IndexError, ValueError):
                    corrupted_count += 1

    if count == 0 and corrupted_count == 0:
        print("No expenses found.")
        return

    print(f"Total number of expenses : {count}")
    print(f"Total amount spent       : ₹{total:.2f}")
    if corrupted_count > 0:
        print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s).")


# ------------------------------------------------
# Function to delete all expenses (reset)
# ------------------------------------------------
def clear_expenses():
    confirm = input("\nAre you sure you want to delete ALL expenses? (yes/no): ").strip().lower()
    if confirm == "yes":
        # Just overwrite the file with nothing (using UTF-8 encoding)
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as f:
            pass
        print("✅ All expenses cleared.")
    else:
        print("Cancelled. No data was deleted.")


# ------------------------------------------------
# Main menu — this is where the program starts
# ------------------------------------------------
def show_menu():
    print("\n╔══════════════════════════════╗")
    print("║      💰 Expense Tracker      ║")
    print("╠══════════════════════════════╣")
    print("║  1. Add Expense              ║")
    print("║  2. View All Expenses        ║")
    print("║  3. View Total Spent         ║")
    print("║  4. Clear All Expenses       ║")
    print("║  5. Exit                     ║")
    print("╚══════════════════════════════╝")


def main():
    print("\nWelcome to Expense Tracker!")
    print("Track your daily expenses easily.\n")

    # Keep the program running until user chooses to exit
    while True:
        show_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            total_expenses()
        elif choice == "4":
            clear_expenses()
        elif choice == "5":
            print("\nGoodbye! Keep tracking your expenses. 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 5.")


# This makes sure main() only runs when we directly run this file
# (not when it's imported somewhere else)
if __name__ == "__main__":
    main()
