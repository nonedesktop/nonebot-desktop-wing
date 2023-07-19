from pathlib import Path
import subprocess
from typing import (
    Iterable, Literal, TypeVar, Union
)

from .constants import WINDOWS

T = TypeVar("T")


def anojoin(args: Iterable[str]) -> str:
    """Like `shlex.join`, but uses dquote (`"`) instead of squote (`'`)."""
    dq, cdq = "\"", "\\\""
    return " ".join([f"\"{s.replace(dq, cdq)}\"" for s in args])


def list_paginate(lst: list[T], sz: int) -> list[list[T]]:
    """
    Cut a list to lists whose length are equal-to-or-less-than a specified
    size.

    - lst: `List[T]`    - a list to be cut.
    - sz: `int`         - max length for cut lists.

    - return: `List[List[T]]`
    """
    return [lst[st:st + sz] for st in range(0, len(lst), sz)]


def system_open(fp: Union[str, Path]) -> subprocess.Popen[bytes]:
    """
    Use system applications to open a file path or URI.

    - fp: `Union[str, Path]`    - a file path or URI.
    - catch_output: `bool`      - whether to catch output stdout and stderr.

    - return: `Popen[bytes]`    - the process running external applications.
    """
    return subprocess.Popen(
        anojoin(("start" if WINDOWS else "xdg-open", str(fp))), shell=True
    )


def perform_pip_command(
    pyexec: str, command: str, *args: str,
    nt_new_win: bool = False, catch_output: bool = False
) -> subprocess.Popen[bytes]:
    """
    Run pip commands.

    - pyexec: `str`             - path to python executable.
    - command: `str`            - pip command.
    - *args: `str`              - args after pip command.
    - nt_new_win: `bool`        - whether to open a new terminal window (nt
                                    only).
    - catch_output: `bool`      - whether to catch output stdout and stderr.

    - return: `Popen[bytes]`    - the process running commands.
    """
    cmd = [pyexec, "-m", "pip", command, *args]
    _flag = 0
    if nt_new_win and WINDOWS:
        _flag = subprocess.CREATE_NEW_CONSOLE
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if catch_output else None,
        stderr=subprocess.STDOUT if catch_output else None,
        creationflags=_flag
    )


def perform_pip_install(
    pyexec: str, *packages: str, update: bool = False, index: str = "",
    nt_new_win: bool = False, catch_output: bool = False
) -> subprocess.Popen[bytes]:
    """
    Run pip install.

    - pyexec: `str`             - path to python executable.
    - *packages: `str`          - packages to be installed.
    - update: `bool`            - whether to update packages.
    - index: `str`              - index for downloading.
    - nt_new_win: `bool`        - whether to open a new terminal window (nt
                                    only).
    - catch_output: `bool`      - whether to catch output stdout and stderr.

    - return: `Popen[bytes]`    - the process running commands.
    """
    args = (*packages,)
    if update:
        args += ("-U",)
    if index:
        args += ("-i", index)
    return perform_pip_command(
        pyexec, "install", *args,
        nt_new_win=nt_new_win,
        catch_output=catch_output
    )


def rrggbb_bg2fg(color: str) -> Literal['#000000', '#ffffff']:
    """
    Convert hex color code background to black or white.

    - color: `str`  - color code with the shape of '#rrggbb'

    - return: `str` - converted color code (`'#000000'` or `'#ffffff'`)
    """
    c_int = int(color[1:], base=16)
    # Formula for choosing color:
    # 0.2126 × R + 0.7152 × G + 0.0722 × B > 0.5
    #   => bright color ==> use opposite dark
    c_bgr: list[int] = []
    for _ in range(3):
        c_bgr.append(c_int & 0xff)
        c_int >>= 8
    b, g, r = (x / 255 for x in c_bgr)
    return (
        "#000000" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 else "#ffffff"
    )