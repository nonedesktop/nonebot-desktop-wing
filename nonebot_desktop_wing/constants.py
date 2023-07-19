import os
import sys

PYPI_MIRRORS: list[str] = [
    "https://pypi.org/simple",
    "https://pypi.doubanio.com/simple",
    "https://mirrors.163.com/pypi/simple",
    "https://mirrors.aliyun.com/pypi/simple",
    "https://mirrors.cloud.tencent.com/pypi/simple",
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.bfsu.edu.cn/pypi/web/simple",
    "https://mirrors.sustech.edu.cn/pypi/simple"
]
"""PyPI mirror lists, including official index, mainly for Chinese (Mainland) users."""

LINUX_TERMINALS: tuple[str, ...] = ("gnome-terminal", "konsole", "xfce4-terminal", "xterm", "st")
"""Some terminal emulators on Linux for choosing."""

WINDOWS: bool = sys.platform.startswith("win") or (sys.platform == "cli" and os.name == "nt")
"""Windows platform identifier."""