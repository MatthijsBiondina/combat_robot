import inspect
import linecache
import os
from pathlib import Path
import random
import socket
import subprocess
import traceback
from multiprocessing import current_process
from typing import Union
import numpy as np
from tqdm import tqdm

bcolors = {
    "PINK": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
}


class UGENT:
    BLUE = "#1E64C8"
    YELLOW = "#FFD200"
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    ORANGE = "#F1A42B"
    RED = "#DC4E28"
    AQUA = "#2D8CA8"
    PINK = "#E85E71"
    SKY = "#8BBEE8"
    LIGHTGREEN = "#AEB050"
    PURPLE = "#825491"
    WARMORANGE = "#FB7E3A"
    TURQUOISE = "#27ABAD"
    LIGHTPURPLE = "#BE5190"
    GREEN = "#71A860"

    COLORS = [
        BLUE,
        YELLOW,
        ORANGE,
        RED,
        AQUA,
        PINK,
        SKY,
        LIGHTGREEN,
        PURPLE,
        WARMORANGE,
        TURQUOISE,
        LIGHTPURPLE,
        GREEN,
    ]

    PRIMARY_COLORS = [BLUE, YELLOW]
    SECONDARY_COLORS = [
        ORANGE,
        RED,
        AQUA,
        PINK,
        SKY,
        LIGHTGREEN,
        PURPLE,
        WARMORANGE,
        TURQUOISE,
        LIGHTPURPLE,
        GREEN,
    ]


def bash(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return output, error


def set_seed(seed):
    """
    Set rng seed for all sources of randomness

    :param seed:
    :return:
    """
    random.seed(seed)
    np.random.seed(seed)


def pretty_string(message: str, color=None, bold=False, underline=False):
    """
    add color and effects to string
    :param message:
    :param color:
    :param bold:
    :param underline:
    :return:
    """
    ou = message
    if color:
        ou = bcolors[color] + message + "\033[0m"
    if bold:
        ou = "\033[1m" + ou + "\033[0m"
    if underline:
        ou = "\033[4m" + ou + "\033[0m"
    return ou


def poem(string):
    if len(string) > 20:
        return string[:20] + "..."
    else:
        return string + " " * (23 - len(string))


def pyout(*message, color="PINK"):
    """
    Print message preceded by traceback, and now including the argument names.
    :param message: The message(s) to print.
    """

    frame = inspect.currentframe().f_back
    line = linecache.getline(frame.f_code.co_filename, frame.f_lineno).strip()

    # Initial approach to find the start of the pyout call
    start_index = line.find("pyout(")
    if start_index == -1:
        arg_str = ""
    else:
        # Count parentheses to find the correct closing one
        count = 0
        for i, char in enumerate(line[start_index:]):
            if char == "(":
                count += 1
            elif char == ")":
                count -= 1
                if count == 0:
                    # Found the matching closing parenthesis
                    arg_str = line[
                              start_index + 6: start_index + i
                              ]  # Exclude "pyout(" and ")"
                    break
        else:
            # Didn't find a matching closing parenthesis (unlikely unless the line is malformed)
            arg_str = line[start_index + 6:]

    trace = traceback.extract_stack()[-2]
    fname = trace.filename.replace(os.path.abspath(os.curdir), "...")
    trace_info = f"{fname}: {trace.name}(...)"

    # Print the argument string, if found
    if arg_str:
        tqdm.write(pretty_string(trace_info, color, bold=True))
        tqdm.write(
            pretty_string(f"ln{trace.lineno}   ", color, bold=True)
            + pretty_string(f"{arg_str} = ...", color, bold=False)
        )
    else:
        tqdm.write(pretty_string(f"{trace_info} - ln{trace.lineno}", color, bold=True))

    # Finally, print the message, if any
    if message:
        message_text = " ".join(str(m) for m in message)
        tqdm.write(message_text)


def pyopen(path, mode):
    pyout(f"{mode} >> {os.path.abspath(path)}", color="BLUE")
    return open(path, mode)


pseudo_random_state = 49


def pynotify(*message):
    message = " ".join(str(m) for m in message)
    trace = traceback.extract_stack()[-2]

    fname = trace.filename.replace(os.path.abspath(os.curdir), "...")

    trace = f"{fname}: {trace.name}(...) - ln{trace.lineno}"

    subprocess.Popen(["notify-send", trace, message])


def prng(decimals=4):
    global pseudo_random_state

    ou = 0
    for ii in range(1, decimals + 1):
        pseudo_random_state = (7 * pseudo_random_state) % 101

        ou += (pseudo_random_state % 10) * 10 ** -ii
    ou = str(ou)[: decimals + 2]

    return float(ou)


def makedirs(path: Union[str, Path]):
    if isinstance(path, Path):
        parts = path.parts
    else:
        parts = path.split("/")

    pth = Path(parts[0])
    os.makedirs(pth, exist_ok=True)
    for folder in parts[1:]:
        pth /= folder
        os.makedirs(pth, exist_ok=True)
    pyout(f"mk >> {os.path.abspath(path)}", color="BLUE")


def listdir(path: str):
    filenames = sorted(os.listdir(path))
    filepaths = [f"{path}/{fname}" for fname in filenames]
    filepaths = [Path(os.path.abspath(path)) for path in filepaths]
    return filepaths


def pbar(iterable, desc="", leave=False, total=None, disable=False):
    # return iterable
    host = socket.gethostname()

    if host in ("AM", "kat", "gorilla"):
        return tqdm(
            iterable,
            desc=poem(desc),
            leave=leave,
            total=total,
            disable=(current_process().name != "MainProcess"),
        )
    else:
        return iterable


def degree_string(angle: float):
    return f"{np.rad2deg(angle):.0f}"


def prog():
    # Get the caller's frame
    caller_frame = inspect.currentframe().f_back
    # Get the filename and line number of the caller
    filename = caller_frame.f_code.co_filename
    line_number = caller_frame.f_lineno

    # Get the previous line from the file
    previous_line = linecache.getline(filename, line_number + 1).strip()

    print(f"ln {line_number}: {previous_line}")

    # Clear the cache and delete the frame to help with garbage collection
    linecache.clearcache()
    del caller_frame


def cursor_up(number_of_lines: int = 1):
    print(f"\033[{number_of_lines}A", end="\r")
