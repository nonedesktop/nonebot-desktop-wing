import os
import sys

PYPI_MIRRORS = [
    "https://pypi.org/simple",
    "https://pypi.doubanio.com/simple",
    "https://mirrors.163.com/pypi/simple",
    "https://mirrors.aliyun.com/pypi/simple",
    "https://mirrors.cloud.tencent.com/pypi/simple",
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.bfsu.edu.cn/pypi/web/simple",
    "https://mirrors.sustech.edu.cn/pypi/simple"
]
LINUX_TERMINALS = ("gnome-terminal", "konsole", "xfce4-terminal", "xterm", "st")
WINDOWS = sys.platform.startswith("win") or (sys.platform == "cli" and os.name == "nt")