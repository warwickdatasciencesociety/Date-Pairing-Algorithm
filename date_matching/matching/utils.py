import os
import math

# def print_terminal_line():
#     t_size = os.get_terminal_size().columns-1
#     print('='*t_size)


def print_terminal_line(title=""):
    title = title.upper()
    t_size = os.get_terminal_size().columns - 1
    string_length = len(title)
    padding = (t_size - string_length) // 2
    print("=" * padding + title + "=" * padding)
