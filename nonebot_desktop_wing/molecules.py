import os
from pathlib import Path
import shlex
from shutil import which
import subprocess
from tempfile import mkstemp
from threading import Lock
from types import ModuleType
from typing import List, Literal, Optional, Tuple, TypeVar, Union, overload

from nonebot_desktop_wing.constants import LINUX_TERMINALS, WINDOWS

_import_lock = Lock()
T = TypeVar("T")


def import_with_lock(
    name: str,
    package: Optional[str] = None
) -> ModuleType:
    from importlib import import_module
    with _import_lock:
        return import_module(name, package)


def list_paginate(lst: List[T], sz: int) -> List[List[T]]:
    return [lst[st:st + sz] for st in range(0, len(lst), sz)]


def get_pause_cmd():
    if WINDOWS:
        return "pause"
    return "read -n1 -p 进程已结束，按任意键关闭。"


def get_terminal_starter():
    if WINDOWS:
        return ("start", "cmd.exe", "/c")
    for te in LINUX_TERMINALS:
        if which(te) is not None:
            return (te, "-e")
    raise FileNotFoundError("no terminal emulator found")


def get_terminal_starter_pure():
    if WINDOWS:
        return ("start", "cmd.exe")
    for te in LINUX_TERMINALS:
        if which(te) is not None:
            return (te,)
    raise FileNotFoundError("no terminal emulator found")


def gen_run_script(cmd: str, cwd: Union[str, Path, None] = None, activate_venv: bool = False):
    fd, fp = mkstemp(".bat" if WINDOWS else ".sh", "nbdtk-")
    if not WINDOWS:
        os.chmod(fd, 0o755)
    with open(fd, "w") as f:
        if not WINDOWS:
            f.write(f"#!/usr/bin/env bash\n")

        if cwd is not None:
            pcwd = Path(cwd)
            if activate_venv and (pcwd / ".venv").exists():
                if WINDOWS:
                    f.write(f"{pcwd / '.venv' / 'Scripts' / 'activate.bat'}\n")
                else:
                    f.write(f"source {pcwd / '.venv' / 'bin' / 'activate'}\n")

            f.write(f"cd \"{cwd}\"\n")
        f.write(f"{cmd}\n")
        f.write(f"{get_pause_cmd()}\n")
    return fp


def exec_new_win(cmd: str, cwd: Union[str, Path, None] = None, *, catch_output: bool = False):
    sname = gen_run_script(cmd, cwd)
    return subprocess.Popen(
        shlex.join((*get_terminal_starter(), sname)), shell=True,
        stdout=subprocess.PIPE if catch_output else None,
        stderr=subprocess.STDOUT if catch_output else None
    ), sname


def open_new_win(cwd: Union[str, Path, None] = None, *, catch_output: bool = False):
    return subprocess.Popen(
        shlex.join(get_terminal_starter_pure()), shell=True, cwd=cwd,
        stdout=subprocess.PIPE if catch_output else None,
        stderr=subprocess.STDOUT if catch_output else None
    )


def system_open(fp: Union[str, Path], *, catch_output: bool = False):
    return subprocess.Popen(
        shlex.join(("start" if WINDOWS else "xdg-open", str(fp))), shell=True,
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
    pyexec: str, command: str, *args: str,
    new_win: Literal[True] = True, catch_output: bool = False
) -> Tuple[subprocess.Popen[bytes], str]:
    ...


def perform_pip_command(
    pyexec: str, command: str, *args: str,
    new_win: bool = False, catch_output: bool = False
):
    cmd = [pyexec, "-m", "pip", command, *args]
    if not new_win:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if catch_output else None,
            stderr=subprocess.STDOUT if catch_output else None
        )
    return exec_new_win(shlex.join(cmd), catch_output=catch_output)


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
):
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


def rrggbb_bg2fg(color: str):
    c_int = int(color[1:], base=16)
    # Formula for choosing color:
    # 0.2126 × R + 0.7152 × G + 0.0722 × B > 0.5 => bright color ==> opposite dark
    c_bgr: List[int] = []
    for _ in range(3):
        c_bgr.append(c_int & 0xff)
        c_int >>= 8
    b, g, r = (x / 255 for x in c_bgr)
    return "#000000" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 else "#ffffff"