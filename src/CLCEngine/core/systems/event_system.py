from typing import Dict, List, Any, Callable, TypeVar, Generic, Optional, Set
import uuid
import inspect

T = TypeVar('T')

class EventArgs:
    """
    事件参数基类，所有事件数据都应继承自这个类
    """
    pass

class EventHandler:
    """
    事件处理器，类似C#中的delegate
    """
    def __init__(self):
        self._callbacks: Set[Callable] = set()
        
    def __iadd__(self, callback: Callable) -> 'EventHandler':
        """
        使用 += 运算符添加事件处理函数
        
        例如: some_event += handler_function
        """
        if not callable(callback):
            raise TypeError("事件处理器必须是可调用对象")
        self._callbacks.add(callback)
        return self
        
    def __isub__(self, callback: Callable) -> 'EventHandler':
        """
        使用 -= 运算符移除事件处理函数
        
        例如: some_event -= handler_function
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)
        return self
        
    def invoke(self, sender: Any, args: EventArgs = None) -> None:
        """
        调用所有注册的处理函数
        
        Args:
            sender: 事件发送者
            args: 事件参数
        """
        if not self._callbacks:
            return
            
        # 创建要调用的处理函数的副本，以便在回调过程中可以安全地添加或删除处理函数
        callbacks = self._callbacks.copy()
        
        for callback in callbacks:
            # 检查回调函数的参数数量，以支持不同签名的回调
            sig = inspect.signature(callback)
            param_count = len(sig.parameters)
            
            if param_count == 0:
                callback()
            elif param_count == 1:
                callback(sender)
            else:
                callback(sender, args)
                
    def has_subscribers(self) -> bool:
        """
        检查是否有订阅者
        
        Returns:
            是否有订阅者
        """
        return len(self._callbacks) > 0
        
    def clear(self) -> None:
        """
        清除所有事件处理函数
        """
        self._callbacks.clear()

class Event(Generic[T]):
    """
    事件类，类似C#中的event
    """
    def __init__(self, name: str = ""):
        self.name = name
        self._handler = EventHandler()
        
    def __iadd__(self, callback: Callable) -> 'Event[T]':
        """
        使用 += 运算符添加事件处理函数
        
        例如: some_event += handler_function
        """
        self._handler += callback
        return self
        
    def __isub__(self, callback: Callable) -> 'Event[T]':
        """
        使用 -= 运算符移除事件处理函数
        
        例如: some_event -= handler_function
        """
        self._handler -= callback
        return self
        
    def invoke(self, sender: Any, args: T = None) -> None:
        """
        调用所有注册的处理函数
        
        Args:
            sender: 事件发送者
            args: 事件参数
        """
        self._handler.invoke(sender, args)
        
    def has_subscribers(self) -> bool:
        """
        检查是否有订阅者
        
        Returns:
            是否有订阅者
        """
        return self._handler.has_subscribers()
        
    def clear(self) -> None:
        """
        清除所有事件处理函数
        """
        self._handler.clear()

class EventSystem:
    """
    事件系统，用于管理全局事件
    """
    _instance: Optional['EventSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventSystem, cls).__new__(cls)
            cls._instance._init_singleton()
        return cls._instance
    
    def _init_singleton(self) -> None:
        """初始化单例"""
        self._events: Dict[str, Event] = {}
        
    def get_event(self, event_name: str) -> Event:
        """
        获取指定名称的事件，如果不存在则创建
        
        Args:
            event_name: 事件名称
            
        Returns:
            事件对象
        """
        if event_name not in self._events:
            self._events[event_name] = Event(event_name)
        return self._events[event_name]
        
    def add_listener(self, event_name: str, callback: Callable) -> None:
        """
        添加事件监听器
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        event = self.get_event(event_name)
        event += callback
        
    def remove_listener(self, event_name: str, callback: Callable) -> None:
        """
        移除事件监听器
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        if event_name in self._events:
            event = self._events[event_name]
            event -= callback
            
    def dispatch_event(self, event_name: str, sender: Any, args: Any = None) -> None:
        """
        分发事件
        
        Args:
            event_name: 事件名称
            sender: 事件发送者
            args: 事件参数
        """
        if event_name in self._events:
            event = self._events[event_name]
            event.invoke(sender, args)
            
    def clear_event(self, event_name: str) -> None:
        """
        清除指定事件的所有监听器
        
        Args:
            event_name: 事件名称
        """
        if event_name in self._events:
            self._events[event_name].clear()
            
    def clear_all_events(self) -> None:
        """
        清除所有事件的监听器
        """
        for event in self._events.values():
            event.clear()

# 一些常用的事件参数类
class ValueChangedEventArgs(EventArgs):
    """
    值改变事件参数
    """
    def __init__(self, old_value: Any, new_value: Any):
        self.old_value = old_value
        self.new_value = new_value

class MouseEventArgs(EventArgs):
    """
    鼠标事件参数
    """
    def __init__(self, position: tuple[int, int], button: int = 0):
        self.position = position
        self.button = button

class KeyEventArgs(EventArgs):
    """
    键盘事件参数
    """
    def __init__(self, key: int, modifiers: int = 0):
        self.key = key
        self.modifiers = modifiers

class CollisionEventArgs(EventArgs):
    """
    碰撞事件参数
    """
    def __init__(self, other: Any):
        self.other = other
        
# 使用示例
"""
# 定义自定义事件参数
class GameStartEventArgs(EventArgs):
    def __init__(self, difficulty: str, player_count: int):
        self.difficulty = difficulty
        self.player_count = player_count

# 创建一个对象，该对象将发出事件
class Game:
    def __init__(self):
        # 定义事件
        self.on_game_start = Event[GameStartEventArgs]("game_start")
        self.on_game_over = Event[EventArgs]("game_over")
        
    def start(self, difficulty: str, player_count: int):
        # 游戏逻辑...
        
        # 触发事件
        args = GameStartEventArgs(difficulty, player_count)
        self.on_game_start.invoke(self, args)
        
    def end(self):
        # 游戏结束逻辑...
        
        # 触发事件，不带参数
        self.on_game_over.invoke(self, None)

# 使用事件
game = Game()

# 添加事件处理函数
def on_game_start_handler(sender, args):
    print(f"游戏已开始，难度：{args.difficulty}，玩家数：{args.player_count}")
    
def on_game_over_handler(sender, args):
    print("游戏结束")

# 订阅事件
game.on_game_start += on_game_start_handler
game.on_game_over += on_game_over_handler

# 调用方法，将触发事件
game.start("普通", 2)
game.end()

# 取消订阅
game.on_game_start -= on_game_start_handler
game.on_game_over -= on_game_over_handler
"""
