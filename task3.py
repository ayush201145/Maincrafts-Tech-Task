import csv
import os
import sys
from datetime import datetime

# Safely reconfigure stdout to avoid UnicodeEncodeError on Windows terminals when printing emojis/rupee symbols
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass

# The file where all expenses are saved
FILE_NAME = "expenses.csv"

# These are the allowed categories (user picks from this list)
CATEGORIES = ["Food", "Travel", "Shopping", "Education", "Health", "Entertainment", "Other"]


# ------------------------------------------------
# Helper function: load all expenses from CSV
# ------------------------------------------------
def load_expenses():
    expenses = []

    # If the file doesn't exist yet, just return empty list
    if not os.path.exists(FILE_NAME):
        return expenses

    with open(FILE_NAME, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:  # skip blank rows
                expenses.append(row)

    return expenses


# ------------------------------------------------
# Helper function: show category menu and get choice
# ------------------------------------------------
def pick_category():
    print("\nAvailable Categories:")
    for i, cat in enumerate(CATEGORIES, start=1):
        print(f"  {i}. {cat}")

    while True:
        choice = input("Pick a category number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        else:
            print("Invalid choice. Please enter a number from the list.")


# ------------------------------------------------
# Function 1: Add a new expense with category
# ------------------------------------------------
def add_expense():
    print("\n--- Add New Expense ---")

    description = input("Enter description (e.g. Lunch, Bus Ticket): ").strip()

    # Validate amount input
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

    # Let user pick a category from the list
    category = pick_category()

    # Save the current date automatically (format: 2025-06-15)
    date_today = datetime.now().strftime("%Y-%m-%d")

    # Append the new expense to the CSV file
    with open(FILE_NAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([description, amount, category, date_today])

    print(f"\n✅ Added: '{description}' | ₹{amount:.2f} | {category} | {date_today}")


# ------------------------------------------------
# Function 2: View all expenses (nicely formatted)
# ------------------------------------------------
def view_all_expenses():
    print("\n--- All Expenses ---")

    expenses = load_expenses()

    if len(expenses) == 0:
        print("No expenses found. Add some first!")
        return

    # Print a table header
    print(f"\n{'No.':<5} {'Description':<20} {'Amount (₹)':>12} {'Category':<15} {'Date'}")
    print("-" * 65)

    corrupted_count = 0
    for i, row in enumerate(expenses, start=1):
        try:
            desc     = row[0]
            amount   = float(row[1])
            category = row[2]
            date     = row[3]
            print(f"{i:<5} {desc:<20} {amount:>12.2f} {category:<15} {date}")
        except (IndexError, ValueError):
            corrupted_count += 1
            print(f"{i:<5} [Corrupted Row]           {'N/A':>12}")

    print("-" * 65)
    if corrupted_count > 0:
        print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s).")


# ------------------------------------------------
# Function 3: Search expenses by category
# ------------------------------------------------
def search_by_category():
    print("\n--- Search by Category ---")

    category = pick_category()
    expenses = load_expenses()

    # Filter rows where category matches
    matching = []
    corrupted_count = 0
    for row in expenses:
        try:
            if row[2].lower() == category.lower():
                # Check that essential fields exist and are valid
                _ = float(row[1])
                _ = row[0]
                _ = row[3]
                matching.append(row)
        except (IndexError, ValueError):
            corrupted_count += 1

    if len(matching) == 0:
        print(f"No expenses found under '{category}'.")
        if corrupted_count > 0:
            print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s) in database.")
        return

    print(f"\nExpenses under '{category}':")
    print(f"\n{'No.':<5} {'Description':<20} {'Amount (₹)':>12} {'Date'}")
    print("-" * 50)

    total = 0.0
    for i, row in enumerate(matching, start=1):
        desc   = row[0]
        amount = float(row[1])
        date   = row[3]
        total += amount
        print(f"{i:<5} {desc:<20} {amount:>12.2f} {date}")

    print("-" * 50)
    print(f"Total spent on {category}: ₹{total:.2f}")
    if corrupted_count > 0:
        print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s) in database.")


# ------------------------------------------------
# Function 4: Total spent per category (summary)
# ------------------------------------------------
def category_summary():
    print("\n--- Spending by Category ---")

    expenses = load_expenses()

    if len(expenses) == 0:
        print("No expenses found.")
        return

    # Use a dictionary to store total per category
    # e.g. { "Food": 500.0, "Travel": 150.0 }
    totals = {}
    corrupted_count = 0

    for row in expenses:
        try:
            cat    = row[2]
            amount = float(row[1])
            # Verify description and date exist
            _ = row[0]
            _ = row[3]

            if cat in totals:
                totals[cat] += amount
            else:
                totals[cat] = amount
        except (IndexError, ValueError):
            corrupted_count += 1

    # Print the summary
    print(f"\n{'Category':<20} {'Total Spent (₹)':>15}")
    print("-" * 38)

    grand_total = 0.0
    for cat, total in totals.items():
        print(f"{cat:<20} {total:>15.2f}")
        grand_total += total

    print("-" * 38)
    print(f"{'GRAND TOTAL':<20} {grand_total:>15.2f}")
    if corrupted_count > 0:
        print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s).")


# ------------------------------------------------
# Function 5: Monthly spending total
# ------------------------------------------------
def monthly_total():
    print("\n--- Monthly Spending ---")

    # Ask user which month they want (format: YYYY-MM)
    month = input("Enter month (format YYYY-MM, e.g. 2025-06): ").strip()

    # Basic format check
    if len(month) != 7 or month[4] != "-":
        print("Invalid format! Please use YYYY-MM (e.g. 2025-06).")
        return

    expenses = load_expenses()

    # Filter expenses where the date starts with the given month
    monthly = []
    corrupted_count = 0
    for row in expenses:
        try:
            if row[3].startswith(month):
                # Verify row items exist and amount is a float
                _ = float(row[1])
                _ = row[0]
                _ = row[2]
                monthly.append(row)
        except (IndexError, ValueError):
            corrupted_count += 1

    if len(monthly) == 0:
        print(f"No expenses found for {month}.")
        if corrupted_count > 0:
            print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s) in database.")
        return

    print(f"\nExpenses for {month}:")
    print(f"\n{'No.':<5} {'Description':<20} {'Amount (₹)':>12} {'Category':<15} {'Date'}")
    print("-" * 65)

    total = 0.0
    for i, row in enumerate(monthly, start=1):
        desc     = row[0]
        amount   = float(row[1])
        category = row[2]
        date     = row[3]
        total   += amount
        print(f"{i:<5} {desc:<20} {amount:>12.2f} {category:<15} {date}")

    print("-" * 65)
    print(f"Total spent in {month}: ₹{total:.2f}")
    if corrupted_count > 0:
        print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s) in database.")


# ------------------------------------------------
# Function 6: Clear all expenses
# ------------------------------------------------
def clear_all():
    confirm = input("\nDelete ALL expenses? This cannot be undone. (yes/no): ").strip().lower()
    if confirm == "yes":
        with open(FILE_NAME, "w", newline="", encoding="utf-8") as f:
            pass  # just overwrite with empty file
        print("✅ All expenses cleared.")
    else:
        print("Cancelled.")


# ------------------------------------------------
# Main menu
# ------------------------------------------------
def show_menu():
    print("\n╔══════════════════════════════════════╗")
    print("║     💰 Expense Tracker 2.0           ║")
    print("╠══════════════════════════════════════╣")
    print("║  1. Add Expense                      ║")
    print("║  2. View All Expenses                ║")
    print("║  3. Search by Category               ║")
    print("║  4. Spending Summary by Category     ║")
    print("║  5. Monthly Spending Total           ║")
    print("║  6. Clear All Expenses               ║")
    print("║  7. Exit                             ║")
    print("╚══════════════════════════════════════╝")


def main():
    print("\nWelcome to Expense Tracker 2.0!")
    print("Now with categories, search, and monthly reports.\n")

    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_all_expenses()
        elif choice == "3":
            search_by_category()
        elif choice == "4":
            category_summary()
        elif choice == "5":
            monthly_total()
        elif choice == "6":
            clear_all()
        elif choice == "7":
            print("\nGoodbye! Stay on top of your expenses. 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 7.")


# Only run main() when this file is executed directly
if __name__ == "__main__":
    main()