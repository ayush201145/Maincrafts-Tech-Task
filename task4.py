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

CSV_FILE = "expenses.csv"
HEADERS = ["id", "date", "description", "amount", "category"]


def ensure_csv():
    # If file doesn't exist, create it with headers
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)
        return

    # Read existing rows to check format
    needs_migration = False
    raw_rows = []
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            raw_rows = list(reader)
    except Exception:
        raw_rows = []

    if not raw_rows:
        # File is empty, write headers
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)
        return

    # Check if the first row matches the header
    first_row = raw_rows[0]
    if len(first_row) != len(HEADERS) or [h.lower().strip() for h in first_row] != [h.lower() for h in HEADERS]:
        needs_migration = True
    else:
        # Check if any row has mismatched column count
        for r in raw_rows[1:]:
            if r and len(r) != len(HEADERS):
                needs_migration = True
                break

    if needs_migration:
        print("⚠️ Legacy database format detected. Migrating 'expenses.csv' to the new schema...")
        migrated_rows = []
        import time
        base_timestamp = int(time.time() * 1000)

        # Check if the first row is a header of some kind
        is_first_header = False
        if len(first_row) == len(HEADERS) and [h.lower().strip() for h in first_row] == [h.lower() for h in HEADERS]:
            is_first_header = True

        data_rows = raw_rows[1:] if is_first_header else raw_rows

        for idx, r in enumerate(data_rows):
            if not r or all(not cell.strip() for cell in r):
                continue

            row_id = str(base_timestamp + idx)

            if len(r) == 2:
                # task2 format: [description, amount]
                desc = r[0].strip()
                amount_str = r[1].strip()
                date = datetime.now().strftime("%Y-%m-%d")
                category = "Other"
            elif len(r) == 4:
                # task3 format: [description, amount, category, date]
                desc = r[0].strip()
                amount_str = r[1].strip()
                category = r[2].strip() if r[2].strip() else "Other"
                date = r[3].strip() if r[3].strip() else datetime.now().strftime("%Y-%m-%d")
            elif len(r) == 5:
                # 5-column but no header or wrong header
                row_id = r[0].strip() if r[0].strip() else row_id
                date = r[1].strip() if r[1].strip() else datetime.now().strftime("%Y-%m-%d")
                desc = r[2].strip()
                amount_str = r[3].strip()
                category = r[4].strip() if r[4].strip() else "Other"
            else:
                # Unknown/fallback
                desc = r[0].strip() if len(r) > 0 else "Unknown"
                amount_str = r[1].strip() if len(r) > 1 else "0.00"
                category = r[2].strip() if len(r) > 2 else "Other"
                date = r[3].strip() if len(r) > 3 else datetime.now().strftime("%Y-%m-%d")

            # Clean and normalize amount
            try:
                amt_val = float(amount_str)
                amount = f"{amt_val:.2f}"
            except ValueError:
                amount = "0.00"

            migrated_rows.append({
                "id": row_id,
                "date": date,
                "description": desc,
                "amount": amount,
                "category": category.title()
            })

        # Write back migrated rows
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(migrated_rows)
        print("✅ Database migration completed successfully.")


def read_expenses():
    ensure_csv()
    rows = []
    corrupted_count = 0
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                try:
                    # Validate all keys exist and are not None
                    r_id = row.get("id")
                    r_date = row.get("date")
                    r_desc = row.get("description")
                    r_amount = row.get("amount")
                    r_cat = row.get("category")
                    
                    if None in (r_id, r_date, r_desc, r_amount, r_cat):
                        raise ValueError("Missing field")
                        
                    # Validate amount is float
                    float(r_amount)
                    rows.append(row)
                except (ValueError, TypeError):
                    corrupted_count += 1
    except Exception as e:
        print(f"Error reading database: {e}")

    if corrupted_count > 0:
        print(f"⚠️ Warning: Skipped {corrupted_count} corrupted or invalid row(s) in database.")

    return rows


def write_expenses(rows):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def add_expense():
    print("\n--- Add New Expense ---")
    
    while True:
        desc = input("Description: ").strip()
        if not desc:
            print("Description cannot be empty. Please enter a description.")
            continue
        break

    while True:
        category = input("Category: ").strip()
        if not category:
            print("Category cannot be empty. Please enter a category.")
            continue
        break

    while True:
        amount_str = input("Amount (in ₹): ").strip()
        try:
            amount = float(amount_str)
            if amount < 0:
                print("Amount cannot be negative! Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Invalid amount! Please enter a valid number.")

    row = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": desc,
        "amount": f"{amount:.2f}",
        "category": category.title()
    }

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(row)

    print(f"✅ Added: '{desc}' | ₹{amount:.2f} | {category.title()} | ID: {row['id']}")


def view_all():
    print("\n--- All Expenses ---")
    rows = read_expenses()

    if not rows:
        print("No expenses found.")
        return

    total = 0.0
    print("\n" + "-" * 85)
    print(f"{'ID':<15} {'DATE':<12} {'DESCRIPTION':<25} {'AMOUNT (₹)':>12} {'CATEGORY'}")
    print("-" * 85)

    for r in rows:
        desc = r['description']
        if len(desc) > 25:
            desc = desc[:22] + "..."
        amount_val = float(r["amount"])
        print(f"{r['id']:<15} {r['date']:<12} {desc:<25} {amount_val:>12.2f} {r['category']}")
        total += amount_val

    print("-" * 85)
    print(f"Records: {len(rows)}")
    print(f"Total Spent: ₹{total:.2f}")


def search_category():
    print("\n--- Search by Category ---")
    category = input("Enter category: ").strip().lower()
    if not category:
        print("Category search term cannot be empty.")
        return

    rows = read_expenses()
    results = [r for r in rows if r["category"].lower() == category]

    if not results:
        print("No matching records found.")
        return

    subtotal = sum(float(r["amount"]) for r in results)

    print("\n" + "-" * 85)
    print(f"{'ID':<15} | {'DATE':<12} | {'DESCRIPTION':<25} | {'AMOUNT (₹)':>12} | {'CATEGORY'}")
    print("-" * 85)

    for r in results:
        desc = r['description']
        if len(desc) > 25:
            desc = desc[:22] + "..."
        amount_val = float(r["amount"])
        print(f"{r['id']:<15} | {r['date']:<12} | {desc:<25} | {amount_val:>12.2f} | {r['category']}")

    print("-" * 85)
    print(f"Category Total: ₹{subtotal:.2f}")


def monthly_total():
    print("\n--- Monthly Spending ---")
    month = input("Enter month (YYYY-MM): ").strip()
    if len(month) != 7 or month[4] != "-":
        print("Invalid format! Please use YYYY-MM (e.g. 2025-06).")
        return

    rows = read_expenses()
    filtered = [r for r in rows if r["date"].startswith(month)]

    if not filtered:
        print(f"No records found for the month {month}.")
        return

    total = sum(float(r["amount"]) for r in filtered)
    print(f"Monthly Total for {month}: ₹{total:.2f}")


def delete_expense():
    print("\n--- Delete Expense ---")
    expense_id = input("Enter Expense ID to delete: ").strip()
    if not expense_id:
        print("Expense ID cannot be empty.")
        return

    rows = read_expenses()
    updated_rows = [r for r in rows if r["id"] != expense_id]

    if len(updated_rows) == len(rows):
        print(f"Expense ID '{expense_id}' not found.")
        return

    write_expenses(updated_rows)
    print(f"✅ Expense with ID '{expense_id}' deleted successfully.")


def run():
    ensure_csv()

    while True:
        print("\n===== EXPENSE TRACKER =====")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Search by Category")
        print("4. Monthly Total")
        print("5. Delete by ID")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_all()
        elif choice == "3":
            search_category()
        elif choice == "4":
            monthly_total()
        elif choice == "5":
            delete_expense()
        elif choice == "6":
            print("\nGoodbye! Keep tracking your expenses. 👋")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    run()
