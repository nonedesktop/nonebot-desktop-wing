from __future__ import annotations
import os
from pathlib import Path
from shutil import which
import subprocess
from tempfile import mkstemp
from threading import Lock
from types import ModuleType
from typing import (
    Iterable, List, Literal, Optional, Tuple, TypeVar, Union, overload
)

from nonebot_desktop_wing.constants import LINUX_TERMINALS, WINDOWS

_import_lock = Lock()
T = TypeVar("T")


def anojoin(args: Iterable[str]) -> str:
    """Like `shlex.join`, but uses dquote (`"`) instead of squote (`'`)."""
    dq, cdq = "\"", "\\\""
    return " ".join([f"\"{s.replace(dq, cdq)}\"" for s in args])


def import_with_lock(
    name: str,
    package: Optional[str] = None
) -> ModuleType:
    """Like `importlib.import_module(...)`, but using a lock to avoid
    conflicts when importing package.
    """
    from importlib import import_module
    with _import_lock:
        return import_module(name, package)


def list_paginate(lst: List[T], sz: int) -> List[List[T]]:
    """
    Cut a list to lists whose length are equal-to-or-less-than a specified
    size.

    - lst: `List[T]`    - a list to be cut.
    - sz: `int`         - max length for cut lists.

    - return: `List[List[T]]`
    """
    return [lst[st:st + sz] for st in range(0, len(lst), sz)]


def get_pause_cmd() -> str:
    """Get pause command on users' platforms."""
    if WINDOWS:
        return "pause"
    return "read -n1 -p 进程已结束，按任意键关闭。"


def get_terminal_starter() -> Tuple[str, ...]:
    """Get args for opening a new window, purposed for executing scripts."""
    if WINDOWS:
        return ("start", "cmd.exe", "/c")
    for te in LINUX_TERMINALS:
        if which(te) is not None:
            return (te, "-e")
    raise FileNotFoundError("no terminal emulator found")


def get_terminal_starter_pure() -> Tuple[str, ...]:
    """Get args for opening a new window, only for opening a new window."""
    if WINDOWS:
        return ("start", "cmd.exe")
    for te in LINUX_TERMINALS:
        if which(te) is not None:
            return (te,)
    raise FileNotFoundError("no terminal emulator found")


def gen_run_script(
    cmd: str, cwd: Union[str, Path, None] = None, activate_venv: bool = False
) -> str:
    """
    Generate executable scripts, for running commands in a new window.

    - cmd: `str`                    - commands to be executed.
    - cwd: `Union[str, Path, None]` - the first work directory to be set.
    - activate_venv: `bool`         - whether to attempt to find and activate
                                      the venv in `cwd`.

    - return: `str`                 - temp script path.
    """
    fd, fp = mkstemp(".bat" if WINDOWS else ".sh", "nbdesktop-")
    if not WINDOWS:
        os.chmod(fd, 0o755)
    with open(fd, "w") as f:
        if not WINDOWS:
            f.write(f"#!/usr/bin/env bash\n")

        if cwd is not None:
            pcwd = Path(cwd)
            if activate_venv and (pcwd / ".venv").exists():
                if WINDOWS:
                    f.write(
                        f"{pcwd / '.venv' / 'Scripts' / 'activate.bat'}\n"
                    )
                else:
                    f.write(f"source {pcwd / '.venv' / 'bin' / 'activate'}\n")

            if WINDOWS:
                # change drive first in cmd.exe
                f.write(f"{pcwd.drive}\n")
            f.write(f"cd \"{cwd}\"\n")
        f.write(f"{cmd}\n")
        f.write(f"{get_pause_cmd()}\n")
    return fp


def exec_nowin(
    cmd: str, cwd: Union[str, Path, None] = None,
    *, catch_output: bool = True
) -> Tuple[subprocess.Popen[bytes], str]:
    """
    Execute commands in a subprocess.
    
    - cmd: `str`                    - commands to be executed.
    - cwd: `Union[str, Path, None]` - the first work directory to be set.
    - catch_output: `bool`          - whether to catch output stdout and
                                      stderr.

    - return: `(Popen[bytes], str)` - the process running commands and temp
                                      script path.
    """
    sname = gen_run_script(cmd, cwd)
    return subprocess.Popen(
        anojoin((*get_terminal_starter(), sname)), shell=True,
        stdout=subprocess.PIPE if catch_output else None,
        stderr=subprocess.STDOUT if catch_output else None
    ), sname


def exec_new_win(
    cmd: str, cwd: Union[str, Path, None] = None
) -> Tuple[subprocess.Popen[bytes], str]:
    """
    Execute commands in a new window.
    
    - cmd: `str`                    - commands to be executed.
    - cwd: `Union[str, Path, None]` - the first work directory to be set.

    - return: `(Popen[bytes], str)` - the process running commands and temp
                                      script path.
    """
    sname = gen_run_script(cmd, cwd)
    return subprocess.Popen(
        anojoin((*get_terminal_starter(), sname)), shell=True,
    ), sname


def open_new_win(
    cwd: Union[str, Path, None] = None
) -> subprocess.Popen[bytes]:
    """
    Open a new terminal window.

    - cwd: `Union[str, Path, None]` - the first work directory to be set.

    - return: `Popen[bytes]`        - the process running new window.
    """
    return subprocess.Popen(
        anojoin(get_terminal_starter_pure()), shell=True, cwd=cwd
    )


def system_open(
    fp: Union[str, Path], *, catch_output: bool = False
) -> subprocess.Popen[bytes]:
    """
    Use system applications to open a file path or URI.

    - fp: `Union[str, Path]`    - a file path or URI.
    - catch_output: `bool`      - whether to catch output stdout and stderr.

    - return: `Popen[bytes]`    - the process running external applications.
    """
    return subprocess.Popen(
        anojoin(("start" if WINDOWS else "xdg-open", str(fp))), shell=True,
        stdout=subprocess.PIPE if catch_output else None,
        stderr=subprocess.STDOUT if catch_output else None
    )


@overload
def perform_pip_command(
    pyexec: str, command: str, *args: str,
    new_win: Literal[False] = False, catch_output: bool = False
) -> subprocess.Popen[bytes]:
    ...


@overload
def perform_pip_command(
    pyexec: str, command: str, *args: str, new_win: Literal[True] = True
) -> Tuple[subprocess.Popen[bytes], str]:
    ...


def perform_pip_command(
    pyexec: str, command: str, *args: str,
    new_win: bool = False, catch_output: bool = False
) -> Union[subprocess.Popen[bytes], Tuple[subprocess.Popen[bytes], str]]:
    """
    Run pip commands.

    - pyexec: `str`         - path to python executable.
    - command: `str`        - pip command.
    - *args: `str`          - args after pip command.
    - new_win: `bool`       - whether to open a new terminal window.
    - catch_output: `bool`  - whether to catch output stdout and stderr.

    - return:               - the process running commands (and temp script
                              path if `new_win` is set `True`).
        - `Popen[bytes] if new_win == False`
        - `(Popen[bytes], str) if new_win == True`
    """
    cmd = [pyexec, "-m", "pip", command, *args]
    if not new_win:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if catch_output else None,
            stderr=subprocess.STDOUT if catch_output else None
        )
    return exec_new_win(anojoin(cmd))


@overload
def perform_pip_install(
    pyexec: str, *packages: str, update: bool = False, index: str = "",
    new_win: Literal[False] = False, catch_output: bool = False
) -> subprocess.Popen[bytes]:
    ...


@overload
def perform_pip_install(
    pyexec: str, *packages: str, update: bool = False, index: str = "",
    new_win: Literal[True] = True, catch_output: bool = False
) -> Tuple[subprocess.Popen[bytes], str]:
    ...


def perform_pip_install(
    pyexec: str, *packages: str, update: bool = False, index: str = "",
    new_win: bool = False, catch_output: bool = False
) -> Union[subprocess.Popen[bytes], Tuple[subprocess.Popen[bytes], str]]:
    """
    Run pip install.

    - pyexec: `str`         - path to python executable.
    - *packages: `str`      - packages to be installed.
    - index: `str`          - index for downloading.
    - new_win: `bool`       - whether to open a new terminal window.
    - catch_output: `bool`  - whether to catch output stdout and stderr.

    - return:               - the process running commands (and temp script
                              path if `new_win` is set `True`).
        - `Popen[bytes] if new_win == False`
        - `(Popen[bytes], str) if new_win == True`
    """
    args = (*packages,)
    if update:
        args += ("-U",)
    if index:
        args += ("-i", index)
    return perform_pip_command(
        pyexec, "install", *args,
        new_win=new_win,  # type: ignore
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
    c_bgr: List[int] = []
    for _ in range(3):
        c_bgr.append(c_int & 0xff)
        c_int >>= 8
    b, g, r = (x / 255 for x in c_bgr)
    return (
        "#000000" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 else "#ffffff"
    )