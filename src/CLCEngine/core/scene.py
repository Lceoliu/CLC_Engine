from typing import Dict, List, Optional, Type, Any, TypeVar, Callable
import pygame
import json
import os

from .gameobject import GameObject

T = TypeVar('T', bound=GameObject)

class Scene:
    """
    场景类，管理游戏中的所有游戏对象。
    一个游戏可以有多个场景，但同一时刻只有一个场景是活跃的。
    """
    def __init__(self, name: str, screen_size: tuple[int, int] = (800, 600)):
        self.name = name
        self.gameobjects: Dict[str, GameObject] = {}  # id -> GameObject
        self.screen_size = screen_size
        self.background_color = (0, 0, 0)  # 默认黑色背景
        self.is_editor_mode = False
        
    def create_gameobject(self, name: str, position: tuple[float, float] = (0, 0)) -> GameObject:
        """创建一个新的游戏对象并添加到场景中"""
        gameobject = GameObject(name, self, position)
        self.add_gameobject(gameobject)
        return gameobject
        
    def add_gameobject(self, gameobject: GameObject) -> None:
        """添加一个游戏对象到场景中"""
        self.gameobjects[gameobject.id] = gameobject
        
    def remove_gameobject(self, gameobject: GameObject) -> None:
        """从场景中移除一个游戏对象"""
        if gameobject.id in self.gameobjects:
            del self.gameobjects[gameobject.id]
            
    def get_gameobject_by_id(self, gameobject_id: str) -> Optional[GameObject]:
        """通过ID获取游戏对象"""
        return self.gameobjects.get(gameobject_id)
        
    def get_gameobjects_by_name(self, name: str) -> List[GameObject]:
        """通过名称获取游戏对象列表"""
        return [obj for obj in self.gameobjects.values() if obj.name == name]
        
    def get_gameobjects_by_type(self, gameobject_type: Type[T]) -> List[T]:
        """获取特定类型的所有游戏对象"""
        return [obj for obj in self.gameobjects.values() if isinstance(obj, gameobject_type)]
        
    def find_gameobjects_with_component(self, component_type: Type) -> List[GameObject]:
        """查找具有特定组件的所有游戏对象"""
        return [obj for obj in self.gameobjects.values() 
                if any(isinstance(comp, component_type) for comp in obj.components)]
        
    def start(self) -> None:
        """初始化场景中的所有游戏对象"""
        for gameobject in list(self.gameobjects.values()):
            if gameobject.active:
                gameobject.start()
                
    def update(self, delta_time: float) -> None:
        """更新场景中的所有游戏对象"""
        for gameobject in list(self.gameobjects.values()):
            if gameobject.active:
                gameobject.update(delta_time)
                
    def fixed_update(self, fixed_delta_time: float) -> None:
        """以固定时间间隔更新场景中的所有游戏对象"""
        for gameobject in list(self.gameobjects.values()):
            if gameobject.active:
                gameobject.fixed_update(fixed_delta_time)
                
    def render(self, screen: pygame.Surface) -> None:
        """渲染场景"""
        # 清空屏幕，使用背景色
        screen.fill(self.background_color)
        
        # TODO: 实现渲染逻辑，按Z轴排序等
        
    def save(self, filepath: str) -> None:
        """将场景保存到文件"""
        data = {
            "name": self.name,
            "screen_size": self.screen_size,
            "background_color": self.background_color,
            "gameobjects": [obj.to_dict() for obj in self.gameobjects.values() if obj.parent is None]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def load(cls, filepath: str) -> 'Scene':
        """从文件加载场景"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        scene = cls(data["name"], data.get("screen_size", (800, 600)))
        scene.background_color = data.get("background_color", (0, 0, 0))
        
        # TODO: 加载游戏对象
        
        return scene
        
    def set_editor_mode(self, enabled: bool) -> None:
        """切换编辑器模式"""
        self.is_editor_mode = enabled
