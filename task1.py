import math

def get_float_input(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_int_input(prompt, min_val=None):
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def addition_task():
    first_value = get_float_input("First number: ")
    second_value = get_float_input("Second number: ")
    result = first_value + second_value
    print(f"Result = {result}")


def parity_checker():
    value = get_int_input("Enter integer: ")
    message = "Even" if value % 2 == 0 else "Odd"
    print(f"{value} is {message}")


def factorial_solver():
    number = get_int_input("Number for factorial: ", min_val=0)
    answer = math.factorial(number)
    print("Factorial value:", answer)


def fibonacci_generator():
    limit = get_int_input("How many terms? ", min_val=0)
    sequence = []
    left, right = 0, 1
    for _ in range(limit):
        sequence.append(str(left))
        left, right = right, left + right
    print(" -> ".join(sequence))


def reverse_text():
    content = input("Enter text: ")
    print("Reversed:", content[::-1])


def palindrome_detector():
    word = input("Enter word: ").strip().lower()
    cleaned_word = "".join(char for char in word if char.isalnum())
    
    if not cleaned_word:
        print("Please enter a valid word or phrase.")
        return

    if cleaned_word == cleaned_word[::-1]:
        print("Palindrome detected")
    else:
        print("Not a palindrome")


def leap_year_identifier():
    input_year = get_int_input("Enter year: ")
    divisible_by_4 = input_year % 4 == 0
    divisible_by_100 = input_year % 100 == 0
    divisible_by_400 = input_year % 400 == 0

    if (divisible_by_4 and not divisible_by_100) or divisible_by_400:
        print("Leap year")
    else:
        print("Normal year")


def armstrong_validator():
    candidate = input("Enter positive integer: ").strip()
    if not candidate.isdigit():
        print("Please enter a valid positive integer.")
        return

    exponent = len(candidate)
    calculated_sum = sum(int(digit) ** exponent for digit in candidate)

    if calculated_sum == int(candidate):
        print("Armstrong number confirmed")
    else:
        print("Not an Armstrong number")


def display_menu():
    print("\n========== TASK MENU ==========")
    print("1 -> Addition")
    print("2 -> Odd/Even")
    print("3 -> Factorial")
    print("4 -> Fibonacci")
    print("5 -> Reverse String")
    print("6 -> Palindrome")
    print("7 -> Leap Year")
    print("8 -> Armstrong Number")
    print("0 -> Quit")


# Defined once globally to avoid recreation on every choice execution
MENU_OPTIONS = {
    "1": addition_task,
    "2": parity_checker,
    "3": factorial_solver,
    "4": fibonacci_generator,
    "5": reverse_text,
    "6": palindrome_detector,
    "7": leap_year_identifier,
    "8": armstrong_validator
}

def execute_choice(selected_option):
    selected_function = MENU_OPTIONS.get(selected_option)
    if selected_function:
        selected_function()
    else:
        print("Please choose a valid option.")


def main():
    while True:
        display_menu()
        user_choice = input("Select option: ").strip()

        if user_choice == "0":
            print("Program terminated.")
            break

        execute_choice(user_choice)


if __name__ == "__main__":
    main()
