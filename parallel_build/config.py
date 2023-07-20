from enum import Enum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from parallel_build.utils import get_app_dir

CONFIG_PATH = Path(get_app_dir("ParallelBuild")) / "config.yaml"


class ProjectSourceType(str, Enum):
    local = "local"
    git = "git"


class ProjectSource(BaseModel):
    type: ProjectSourceType
    value: str

    class Config:
        use_enum_values = True


class BuildTarget(str, Enum):
    windows = "Windows"
    windows64 = "Windows 64"
    macos = "OSXUniversal"
    linux = "Linux64"
    webgl = "WebGL"


class ProjectBuildConfig(BaseModel):
    target: BuildTarget = BuildTarget.webgl
    path: str = "Build/WebGL"

    class Config:
        use_enum_values = True


class ProjectPostBuildAction(BaseModel):
    action: Literal["copy", "publish-itch"]
    params: dict[str, str] | None


class Project(BaseModel):
    name: str
    source: ProjectSource
    build: ProjectBuildConfig = ProjectBuildConfig()
    post_build: list[ProjectPostBuildAction] = []


class Config(BaseModel):
    projects: list[Project] = []
    git_polling_interval: int = 30

    @classmethod
    def load(cls):
        if not CONFIG_PATH.exists():
            CONFIG_PATH.parent.mkdir(exist_ok=True)
            CONFIG_PATH.touch()
        with open(
            CONFIG_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            config = yaml.safe_load(file.read())
            if not config:
                return cls()
        return cls.model_validate(config)

    @classmethod
    def loads(cls, config_str: str):
        config = yaml.safe_load(config_str)
        return cls.model_validate(config)

    def save(self):
        yaml_config = yaml.safe_dump(self.model_dump())
        with open(
            CONFIG_PATH,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(yaml_config)
