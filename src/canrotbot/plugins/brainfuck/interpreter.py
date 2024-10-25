def execute(
    code: str,
    input_data: str = "",
    stack_size: int = 255,
    max_number: int = 255,
    max_steps: int = 2**32,
) -> str:
    steps: int = 0
    data_stack: list[int] = [0] * stack_size
    data_pointer: int = 0
    code_pointer: int = 0
    input_pointer: int = 0
    execute_result: str = ""

    while code_pointer < len(code):
        if steps >= max_steps:
            raise RuntimeError("The program is too long.")

        symbol = code[code_pointer]

        if symbol == "[" and data_stack[data_pointer] == 0:
            level = 0
            while True:
                symbol = code[code_pointer]
                if symbol == "[":
                    level += 1
                elif symbol == "]":
                    level -= 1
                code_pointer += 1
                if level == 0:
                    break
        elif symbol == "]" and data_stack[data_pointer] != 0:
            level = 0
            while True:
                symbol = code[code_pointer]
                if symbol == "]":
                    level += 1
                elif symbol == "[":
                    level -= 1
                code_pointer -= 1
                if level == 0:
                    break

        if symbol == ">":
            data_pointer += 1
        elif symbol == "<":
            data_pointer -= 1
        elif symbol == "+":
            data_stack[data_pointer] = (data_stack[data_pointer] + 1) % max_number
        elif symbol == "-":
            data_stack[data_pointer] = (data_stack[data_pointer] - 1) % max_number
        elif symbol == ".":
            execute_result += chr(data_stack[data_pointer])
        elif symbol == ",":
            if input_pointer >= len(input_data):
                raise ValueError("Input data is not enough")
            data = input_data[input_pointer]
            input_pointer += 1
            data_stack[data_pointer] = ord(data)

        code_pointer += 1
        steps += 1

    return execute_result
