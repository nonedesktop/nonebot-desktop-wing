from __future__ import annotations
import asyncio
from glob import glob
from pathlib import Path
import sys
from typing import TYPE_CHECKING, List, Optional, Union

from dotenv.main import DotEnv

from nonebot_desktop_wing.constants import WINDOWS
from nonebot_desktop_wing.lazylib import nb_cli
from nonebot_desktop_wing.molecules import perform_pip_install

if TYPE_CHECKING:
    from nb_cli.config import Driver, Adapter


def find_python(fp: Union[str, Path]) -> Path:
    pfp = Path(fp)
    veexec = (
        pfp / ".venv"
        / ("Scripts" if WINDOWS else "bin")
        / ("python.exe" if WINDOWS else "python")
    )
    return veexec if veexec.exists() else Path(sys.executable)


def distributions(*fp: str):
    from importlib import metadata
    if fp:
        return metadata.distributions(path=list(fp))
    return metadata.distributions()


def getdist(root: str):
    return (
        distributions(
            *(str(Path(root) / si)
            for si in glob(".venv/**/site-packages", root_dir=root, recursive=True))
        )
    )


def create(
    fp: str,
    drivers: List[Driver],
    adapters: List[Adapter],
    dev: bool,
    usevenv: bool,
    index: Optional[str] = None
):
    p = Path(fp)
    if p.exists():
        p.rmdir()
    nb_cli.handlers.create_project(
        "simple" if dev else "bootstrap",
        {
            "nonebot": {
                "project_name": p.name,
                "drivers": [d.dict() for d in drivers],
                "adapters": [a.dict() for a in adapters],
                "use_src": True
            }
        },
        str(p.parent)
    )
    dri_real = [d.project_link for d in drivers]
    adp_real = [a.project_link for a in adapters]
    dir_name = p.name.replace(" ", "-")
    venv_dir = p / ".venv"

    if usevenv:
        from venv import create as create_venv
        create_venv(venv_dir, prompt=dir_name, with_pip=True)

    pyexec = find_python(p)

    ret = perform_pip_install(
        str(pyexec), "nonebot2", *dri_real, *adp_real, index=index or ""
    )

    if ret.returncode != 0:
        raise OSError("cannot install packages")


def get_builtin_plugins(pypath: str):
    return asyncio.run(nb_cli.handlers.list_builtin_plugins(python_path=pypath))


def find_env_file(fp: Union[str, Path]):
    return glob(".env*", root_dir=fp)


def get_env_config(ep: Path, config: str):
    return DotEnv(ep).get(config)


def recursive_find_env_config(fp: Union[str, Path], config: str):
    pfp = Path(fp)
    cp = pfp / ".env"
    if not cp.is_file():
        return get_env_config(pfp / ".env.prod", config)
    glb = DotEnv(cp).dict()
    if config in glb:
        return glb[config]
    env = glb.get("ENVIRONMENT", None)
    return env and get_env_config(pfp / f".env.{env}", config)


def recursive_update_env_config(fp: Union[str, Path], config: str, value: str):
    pfp = Path(fp)
    cp = pfp / ".env"
    if not cp.is_file():
        cp = pfp / ".env.prod"
        useenv = DotEnv(cp).dict()
    else:
        useenv = DotEnv(cp).dict()
        if config not in useenv:
            env = get_env_config(cp, "ENVIRONMENT")
            if env:
                cenv = DotEnv(pfp / f".env.{env}").dict()
                if config in cenv:
                    cp = pfp / f".env.{env}"
                    useenv = cenv

    useenv.update({config: value})

    with open(cp, "w") as f:
        f.writelines(f"{k}={v}\n" for k, v in useenv.items() if k and v)


def get_toml_config(basedir: Union[str, Path]):
    basepath = Path(basedir)
    return nb_cli.config.ConfigManager(str(find_python(basepath)), basepath / "pyproject.toml")