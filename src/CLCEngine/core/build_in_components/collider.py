from typing import Dict, Any, List, Optional, Tuple, Type, Callable
import pygame
from ..component import Component
from .transform import Transform

class Collider(Component):
    """
    碰撞器组件基类，用于碰撞检测。
    """
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.is_trigger = False  # 是否只触发事件而不产生物理碰撞
        self.layer = 0  # 碰撞层，用于过滤碰撞
        self.on_collision_enter_callbacks: List[Callable[['Collider'], None]] = []
        self.on_collision_exit_callbacks: List[Callable[['Collider'], None]] = []
        self.current_collisions: List['Collider'] = []
        
    def on_collision_enter(self, other: 'Collider') -> None:
        """当开始碰撞时调用"""
        for callback in self.on_collision_enter_callbacks:
            callback(other)
            
    def on_collision_exit(self, other: 'Collider') -> None:
        """当结束碰撞时调用"""
        for callback in self.on_collision_exit_callbacks:
            callback(other)
            
    def add_collision_enter_callback(self, callback: Callable[['Collider'], None]) -> None:
        """添加碰撞开始回调"""
        self.on_collision_enter_callbacks.append(callback)
        
    def add_collision_exit_callback(self, callback: Callable[['Collider'], None]) -> None:
        """添加碰撞结束回调"""
        self.on_collision_exit_callbacks.append(callback)
        
    def is_colliding_with(self, other: 'Collider') -> bool:
        """检测是否与另一个碰撞器碰撞，子类应重写此方法"""
        raise NotImplementedError("子类应实现此方法")
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化到字典"""
        data = super().to_dict()
        data.update({
            "is_trigger": self.is_trigger,
            "layer": self.layer
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], gameobject) -> 'Collider':
        """从字典反序列化"""
        collider = super().from_dict(data, gameobject)
        collider.is_trigger = data.get("is_trigger", False)
        collider.layer = data.get("layer", 0)
        return collider
        
class BoxCollider(Collider):
    """
    矩形碰撞器
    """
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.width = 100
        self.height = 100
        self.offset = pygame.Vector2(0, 0)  # 相对于游戏对象位置的偏移
        
    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        transform = self.gameobject.get_component(Transform)
        if transform is None:
            return pygame.Rect(0, 0, self.width, self.height)
            
        world_pos = transform.get_world_position()
        world_scale = transform.get_world_scale()
        
        scaled_width = self.width * world_scale.x
        scaled_height = self.height * world_scale.y
        
        # 考虑旋转的情况下，简化为AABB (Axis-Aligned Bounding Box)
        return pygame.Rect(
            world_pos.x + self.offset.x - scaled_width / 2,
            world_pos.y + self.offset.y - scaled_height / 2,
            scaled_width,
            scaled_height
        )
        
    def is_colliding_with(self, other: 'Collider') -> bool:
        """检测是否与另一个碰撞器碰撞"""
        if isinstance(other, BoxCollider):
            return self.get_rect().colliderect(other.get_rect())
        elif isinstance(other, CircleCollider):
            return pygame.Rect.collidepoint(self.get_rect(), other.get_center()) or \
                   self._rect_circle_collision(self.get_rect(), other.get_center(), other.get_radius())
        return False
        
    def _rect_circle_collision(self, rect: pygame.Rect, circle_center: Tuple[float, float], 
                              circle_radius: float) -> bool:
        """矩形与圆的碰撞检测"""
        # 找到矩形上离圆心最近的点
        closest_x = max(rect.left, min(circle_center[0], rect.right))
        closest_y = max(rect.top, min(circle_center[1], rect.bottom))
        
        # 计算圆心到最近点的距离
        distance_x = circle_center[0] - closest_x
        distance_y = circle_center[1] - closest_y
        
        # 如果距离小于半径，则发生碰撞
        return (distance_x ** 2 + distance_y ** 2) < (circle_radius ** 2)
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化到字典"""
        data = super().to_dict()
        data.update({
            "width": self.width,
            "height": self.height,
            "offset": (self.offset.x, self.offset.y)
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], gameobject) -> 'BoxCollider':
        """从字典反序列化"""
        collider = super().from_dict(data, gameobject)
        collider.width = data.get("width", 100)
        collider.height = data.get("height", 100)
        offset = data.get("offset", (0, 0))
        collider.offset = pygame.Vector2(offset[0], offset[1])
        return collider
        
class CircleCollider(Collider):
    """
    圆形碰撞器
    """
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.radius = 50
        self.offset = pygame.Vector2(0, 0)  # 相对于游戏对象位置的偏移
        
    def get_center(self) -> Tuple[float, float]:
        """获取世界坐标中的圆心位置"""
        transform = self.gameobject.get_component(Transform)
        if transform is None:
            return (0, 0)
            
        world_pos = transform.get_world_position()
        return (world_pos.x + self.offset.x, world_pos.y + self.offset.y)
        
    def get_radius(self) -> float:
        """获取世界坐标中的半径"""
        transform = self.gameobject.get_component(Transform)
        if transform is None:
            return self.radius
            
        world_scale = transform.get_world_scale()
        # 使用x和y缩放的平均值
        return self.radius * (world_scale.x + world_scale.y) / 2
        
    def is_colliding_with(self, other: 'Collider') -> bool:
        """检测是否与另一个碰撞器碰撞"""
        if isinstance(other, CircleCollider):
            # 圆与圆的碰撞
            center1 = self.get_center()
            center2 = other.get_center()
            
            distance_squared = (center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2
            combined_radius = self.get_radius() + other.get_radius()
            
            return distance_squared < (combined_radius ** 2)
        elif isinstance(other, BoxCollider):
            # 圆与矩形的碰撞
            return other.is_colliding_with(self)
        return False
        
    def to_dict(self) -> Dict[str, Any]:
        """序列化到字典"""
        data = super().to_dict()
        data.update({
            "radius": self.radius,
            "offset": (self.offset.x, self.offset.y)
        })
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], gameobject) -> 'CircleCollider':
        """从字典反序列化"""
        collider = super().from_dict(data, gameobject)
        collider.radius = data.get("radius", 50)
        offset = data.get("offset", (0, 0))
        collider.offset = pygame.Vector2(offset[0], offset[1])
        return collider
