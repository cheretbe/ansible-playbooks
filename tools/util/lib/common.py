import sys
import PyInquirer

def read_input(message, default_val, is_password=False):
    answers = PyInquirer.prompt(
        questions=[
            {
                "type": "password" if is_password else "input",
                "name": "value",
                "message": message,
                "default": "" if default_val is None else default_val
            }
        ]
    )
    if not answers:
        sys.exit(1)
    return answers["value"]

def select_from_list(message, choices):
    answers = PyInquirer.prompt([
        {
            "type": "list",
            "name": "selection",
            "message": message,
            # Doesn't work for now. See https://github.com/CITGuru/PyInquirer/issues/17
            # and https://github.com/CITGuru/PyInquirer/issues/90
            # "default": 2,
            "choices": choices
        }
    ])
    if not answers:
        sys.exit(1)

    return answers["selection"]
