import uuid
from typing import Dict, List, Optional, Type, TypeVar, Any, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .scene import Scene
    from .component import Component

T = TypeVar('T', bound='Component')

class GameObject:
    """
    游戏对象类，是游戏中所有实体的基础。
    游戏对象可以附加多个组件以实现不同的功能。
    """
    def __init__(self, name: str, scene: 'Scene', position: tuple[float, float] = (0, 0)):
        self.id = str(uuid.uuid4())
        self.name = name
        self.scene = scene
        self.components: List['Component'] = []
        self.active = True
        self.position = position
        self.children: List['GameObject'] = []
        self.parent: Optional['GameObject'] = None
        
    def add_component(self, component_type: Type[T], **kwargs) -> T:
        """添加一个组件到游戏对象"""
        from .component import Component
        
        if not issubclass(component_type, Component):
            raise TypeError(f"组件类型必须是Component的子类")
            
        component = component_type(self, **kwargs)
        self.components.append(component)
        return component
        
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """获取指定类型的组件"""
        for component in self.components:
            if isinstance(component, component_type):
                return component
        return None
        
    def get_components(self, component_type: Type[T]) -> List[T]:
        """获取所有指定类型的组件"""
        return [c for c in self.components if isinstance(c, component_type)]
        
    def remove_component(self, component: 'Component') -> None:
        """移除指定的组件"""
        if component in self.components:
            component.on_destroy()
            self.components.remove(component)
            
    def add_child(self, child: 'GameObject') -> None:
        """添加子游戏对象"""
        if child.parent:
            child.parent.children.remove(child)
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'GameObject') -> None:
        """移除子游戏对象"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def start(self) -> None:
        """初始化游戏对象，调用所有组件的start方法"""
        for component in self.components:
            if component.enabled:
                component.start()
                
        for child in self.children:
            if child.active:
                child.start()
                
    def update(self, delta_time: float) -> None:
        """更新游戏对象，调用所有组件的update方法"""
        if not self.active:
            return
            
        for component in self.components:
            if component.enabled:
                component.update(delta_time)
                
        for child in self.children:
            child.update(delta_time)
            
    def fixed_update(self, fixed_delta_time: float) -> None:
        """固定时间间隔更新，调用所有组件的fixed_update方法"""
        if not self.active:
            return
            
        for component in self.components:
            if component.enabled:
                component.fixed_update(fixed_delta_time)
                
        for child in self.children:
            child.fixed_update(fixed_delta_time)
            
    def destroy(self) -> None:
        """销毁游戏对象"""
        # 先销毁所有子对象
        for child in self.children[:]:  # 使用副本避免在迭代过程中修改列表
            child.destroy()
            
        # 调用所有组件的on_destroy方法
        for component in self.components:
            component.on_destroy()
            
        # 从父对象中移除
        if self.parent:
            self.parent.remove_child(self)
            
        # 从场景中移除
        self.scene.remove_gameobject(self)
        
    def to_dict(self) -> Dict[str, Any]:
        """将游戏对象序列化为字典，用于保存/加载"""
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "position": self.position,
            "components": [comp.to_dict() for comp in self.components],
            "children": [child.to_dict() for child in self.children]
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], scene: 'Scene') -> 'GameObject':
        """从字典中反序列化游戏对象"""
        obj = cls(data["name"], scene, data.get("position", (0, 0)))
        obj.id = data.get("id", obj.id)
        obj.active = data.get("active", True)
        
        # TODO: 加载组件和子对象
        
        return obj
