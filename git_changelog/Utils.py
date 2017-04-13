from re import match, IGNORECASE
from tzlocal import get_localzone
from datetime import datetime


def match_any_pattern(text, patterns):
    for pattern in patterns:
        if match(string=text, pattern=pattern, flags=IGNORECASE):
            return True
    return False


def max_by_lambda(collection, func):
    max_item = collection[0]
    for item in collection[1:]:
        if func(item) > func(max_item):
            max_item = item
    return max_item


def ask_question(prompt, default_answer):
    answer = raw_input(prompt)
    return answer if answer else default_answer


def local_datetime():
    return datetime.now(tz=get_localzone())
