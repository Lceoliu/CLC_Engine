from typing import Dict, Any, Tuple, Optional
import math
import pygame
from ..component import Component

class Transform(Component):
    """
    变换组件，处理游戏对象的位置、旋转和缩放。
    每个GameObject默认都会有一个Transform组件。
    """
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.position = pygame.Vector2(0, 0)
        self.rotation = 0.0  # 角度制，顺时针
        self.scale = pygame.Vector2(1, 1)
        self.z_index = 0  # 用于渲染排序
        
    def translate(self, x: float, y: float) -> None:
        """移动物体"""
        self.position.x += x
        self.position.y += y
        
    def set_position(self, x: float, y: float) -> None:
        """设置物体位置"""
        self.position.x = x
        self.position.y = y
        
    def rotate(self, angle: float) -> None:
        """旋转物体（角度制）"""
        self.rotation = (self.rotation + angle) % 360
        
    def set_rotation(self, angle: float) -> None:
        """设置物体旋转角度（角度制）"""
        self.rotation = angle % 360
        
    def set_scale(self, x: float, y: float) -> None:
        """设置物体缩放"""
        self.scale.x = x
        self.scale.y = y
        
    def get_forward(self) -> pygame.Vector2:
        """获取前方向向量"""
        rad = math.radians(self.rotation)
        return pygame.Vector2(math.cos(rad), math.sin(rad))
        
    def get_right(self) -> pygame.Vector2:
        """获取右方向向量"""
        rad = math.radians(self.rotation + 90)
        return pygame.Vector2(math.cos(rad), math.sin(rad))
        
    def get_world_position(self) -> pygame.Vector2:
        """获取世界坐标"""
        if self.gameobject.parent is None:
            return pygame.Vector2(self.position)
            
        parent_transform = self.gameobject.parent.get_component(Transform)
        if parent_transform is None:
            return pygame.Vector2(self.position)
            
        # 考虑父对象的位置、旋转和缩放
        parent_pos = parent_transform.get_world_position()
        parent_rot = parent_transform.get_world_rotation()
        parent_scale = parent_transform.get_world_scale()
        
        # 旋转和缩放的相对位置
        rad = math.radians(parent_rot)
        rot_x = self.position.x * math.cos(rad) - self.position.y * math.sin(rad)
        rot_y = self.position.x * math.sin(rad) + self.position.y * math.cos(rad)
        
        return pygame.Vector2(
            parent_pos.x + rot_x * parent_scale.x,
            parent_pos.y + rot_y * parent_scale.y
        )
        
    def get_world_rotation(self) -> float:
        """获取世界旋转角度"""
        if self.gameobject.parent is None:
            return self.rotation
            
        parent_transform = self.gameobject.parent.get_component(Transform)
        if parent_transform is None:
            return self.rotation
            
        return (parent_transform.get_world_rotation() + self.rotation) % 360
        
    def get_world_scale(self) -> pygame.Vector2:
        """获取世界缩放"""
        if self.gameobject.parent is None:
            return pygame.Vector2(self.scale)
            
        parent_transform = self.gameobject.parent.get_component(Transform)
        if parent_transform is None:
            return pygame.Vector2(self.scale)
            
        parent_scale = parent_transform.get_world_scale()
        return pygame.Vector2(self.scale.x * parent_scale.x, self.scale.y * parent_scale.y)
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化到字典"""
        data = super().to_dict()
        data.update({
            "position": (self.position.x, self.position.y),
            "rotation": self.rotation,
            "scale": (self.scale.x, self.scale.y),
            "z_index": self.z_index
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], gameobject) -> 'Transform':
        """从字典反序列化"""
        transform = super().from_dict(data, gameobject)
        pos = data.get("position", (0, 0))
        scale = data.get("scale", (1, 1))
        
        transform.position = pygame.Vector2(pos[0], pos[1])
        transform.rotation = data.get("rotation", 0)
        transform.scale = pygame.Vector2(scale[0], scale[1])
        transform.z_index = data.get("z_index", 0)
        
        return transform
