

def input_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def input_str(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: строка не может быть пустой.")
