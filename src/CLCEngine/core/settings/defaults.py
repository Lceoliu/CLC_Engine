__all__ = [
    "DefaultSettings",
    "DefaultPath",
]
import os

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path

def find_clc_engine_path(start_dir: Path = Path(__file__).resolve()):
    """
    从当前文件所在路径开始，一直向上查找父路径，
    直到找到文件夹名为 "CLC Engine"。
    """
    for parent in [start_dir] + list(start_dir.parents):
        if parent.name == "CLC Engine":
            return parent
    raise FileNotFoundError("无法找到名为 'CLC Engine' 的文件夹。")

try:
    BASE_PATH = find_clc_engine_path()
    SRC_CLC_PATH = os.path.join(BASE_PATH, "src", "CLCEngine")
    import sys
    if SRC_CLC_PATH not in sys.path:
        sys.path.append(SRC_CLC_PATH)
except FileNotFoundError:
    exit("无法找到名为 'CLC Engine' 的文件夹。请确保脚本在正确的目录中运行。")
    
@dataclass
class DefaultSettings:
    """
    默认设置类，用于存储游戏引擎的默认设置
    """
    screen_size: Tuple[int, int] = (800, 600)
    title: str = "CLC Engine"
    is_editor_mode: bool = True
    is_paused: bool = False
    is_fullscreen: bool = False
    background_color: Tuple[int, int, int] = (0, 0, 0)
    frame_rate: int = 60
    assets_path: str = "assets"
    scenes_path: str = "scenes"
    ui_path: str = "ui"
    font_name: str = "microsoftyahei"
    font_size: int = 24
    
@dataclass
class DefaultPath:
    """
    默认路径类，用于存储游戏引擎的默认路径
    """
    editor_config_path: str = os.path.join(SRC_CLC_PATH, "configs")
    editor_ui_themes_path: str = os.path.join(editor_config_path, "editor_ui_themes")