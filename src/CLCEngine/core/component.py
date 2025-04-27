from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .gameobject import GameObject

class Component:
    """
    组件基类，所有组件都应该继承自这个类。
    组件是附加到游戏对象上的功能单元。
    """
    def __init__(self, gameobject: 'GameObject'):
        self.gameobject = gameobject
        self.enabled = True
        
    def start(self) -> None:
        """当组件首次启用时调用"""
        pass
        
    def update(self, delta_time: float) -> None:
        """每帧调用"""
        pass
        
    def fixed_update(self, fixed_delta_time: float) -> None:
        """固定时间间隔调用，用于物理计算等"""
        pass
        
    def on_destroy(self) -> None:
        """当组件被销毁时调用"""
        pass
        
    def to_dict(self) -> Dict[str, Any]:
        """将组件序列化为字典，用于保存/加载"""
        return {
            "type": self.__class__.__name__,
            "enabled": self.enabled
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any], gameobject: 'GameObject') -> 'Component':
        """从字典中反序列化组件"""
        component = cls(gameobject)
        component.enabled = data.get("enabled", True)
        return component
