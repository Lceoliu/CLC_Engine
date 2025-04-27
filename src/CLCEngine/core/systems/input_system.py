import pygame
from typing import Dict, Set, Tuple, Optional, List, Callable

class InputSystem:
    """
    输入系统，管理键盘、鼠标和控制器的输入
    """
    _instance: Optional['InputSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InputSystem, cls).__new__(cls)
            cls._instance._init_singleton()
        return cls._instance
    
    def _init_singleton(self):
        """初始化单例"""
        self.keys_pressed: Set[int] = set()  # 当前按下的键
        self.keys_down: Set[int] = set()  # 这一帧新按下的键
        self.keys_up: Set[int] = set()  # 这一帧释放的键
        
        self.mouse_position = (0, 0)
        self.mouse_delta = (0, 0)
        self.mouse_buttons_pressed: Set[int] = set()  # 当前按下的鼠标按钮
        self.mouse_buttons_down: Set[int] = set()  # 这一帧新按下的鼠标按钮
        self.mouse_buttons_up: Set[int] = set()  # 这一帧释放的鼠标按钮
        self.mouse_wheel_delta = 0
        
        self.on_key_down_callbacks: Dict[int, List[Callable[[], None]]] = {}
        self.on_key_up_callbacks: Dict[int, List[Callable[[], None]]] = {}
        self.on_mouse_down_callbacks: Dict[int, List[Callable[[Tuple[int, int]], None]]] = {}
        self.on_mouse_up_callbacks: Dict[int, List[Callable[[Tuple[int, int]], None]]] = {}
        
        self.axis_mappings: Dict[str, List[Tuple[int, int, float]]] = {}  # 轴映射，键->值
        
    def update(self, events: Optional[List[pygame.event.Event]] = None) -> None:
        """更新输入状态，每帧调用"""
        # 清除上一帧的状态
        self.keys_down.clear()
        self.keys_up.clear()
        self.mouse_buttons_down.clear()
        self.mouse_buttons_up.clear()
        self.mouse_wheel_delta = 0
        
        # 处理事件
        for event in events or pygame.event.get():
            if not isinstance(event, pygame.event.Event):
                continue
            if event.type == pygame.QUIT:
                # 处理退出事件
                pass
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key not in self.keys_pressed:
                    self.keys_pressed.add(key)
                    self.keys_down.add(key)
                    self._trigger_key_down_callbacks(key)
            elif event.type == pygame.KEYUP:
                key = event.key
                if key in self.keys_pressed:
                    self.keys_pressed.remove(key)
                    self.keys_up.add(key)
                    self._trigger_key_up_callbacks(key)
            elif event.type == pygame.MOUSEMOTION:
                prev_position = self.mouse_position
                self.mouse_position = event.pos
                self.mouse_delta = (
                    self.mouse_position[0] - prev_position[0],
                    self.mouse_position[1] - prev_position[1]
                )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                button = event.button
                if button not in self.mouse_buttons_pressed:
                    self.mouse_buttons_pressed.add(button)
                    self.mouse_buttons_down.add(button)
                    self._trigger_mouse_down_callbacks(button, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                button = event.button
                if button in self.mouse_buttons_pressed:
                    self.mouse_buttons_pressed.remove(button)
                    self.mouse_buttons_up.add(button)
                    self._trigger_mouse_up_callbacks(button, event.pos)
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel_delta = event.y
                
    def _trigger_key_down_callbacks(self, key: int):
        """触发按键按下回调"""
        if key in self.on_key_down_callbacks:
            for callback in self.on_key_down_callbacks[key]:
                callback()
                
    def _trigger_key_up_callbacks(self, key: int):
        """触发按键释放回调"""
        if key in self.on_key_up_callbacks:
            for callback in self.on_key_up_callbacks[key]:
                callback()
                
    def _trigger_mouse_down_callbacks(self, button: int, position: Tuple[int, int]):
        """触发鼠标按下回调"""
        if button in self.on_mouse_down_callbacks:
            for callback in self.on_mouse_down_callbacks[button]:
                callback(position)
                
    def _trigger_mouse_up_callbacks(self, button: int, position: Tuple[int, int]):
        """触发鼠标释放回调"""
        if button in self.on_mouse_up_callbacks:
            for callback in self.on_mouse_up_callbacks[button]:
                callback(position)
                
    def is_key_pressed(self, key: int) -> bool:
        """检查按键是否按下"""
        return key in self.keys_pressed
        
    def is_key_down(self, key: int) -> bool:
        """检查按键是否在这一帧按下"""
        return key in self.keys_down
        
    def is_key_up(self, key: int) -> bool:
        """检查按键是否在这一帧释放"""
        return key in self.keys_up
        
    def is_mouse_button_pressed(self, button: int) -> bool:
        """检查鼠标按钮是否按下"""
        return button in self.mouse_buttons_pressed
        
    def is_mouse_button_down(self, button: int) -> bool:
        """检查鼠标按钮是否在这一帧按下"""
        return button in self.mouse_buttons_down
        
    def is_mouse_button_up(self, button: int) -> bool:
        """检查鼠标按钮是否在这一帧释放"""
        return button in self.mouse_buttons_up
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标位置"""
        return self.mouse_position
        
    def get_mouse_delta(self) -> Tuple[int, int]:
        """获取鼠标移动增量"""
        return self.mouse_delta
        
    def get_mouse_wheel_delta(self) -> int:
        """获取鼠标滚轮增量"""
        return self.mouse_wheel_delta
        
    def add_on_key_down_callback(self, key: int, callback: Callable[[], None]) -> None:
        """添加按键按下回调"""
        if key not in self.on_key_down_callbacks:
            self.on_key_down_callbacks[key] = []
        self.on_key_down_callbacks[key].append(callback)
        
    def add_on_key_up_callback(self, key: int, callback: Callable[[], None]) -> None:
        """添加按键释放回调"""
        if key not in self.on_key_up_callbacks:
            self.on_key_up_callbacks[key] = []
        self.on_key_up_callbacks[key].append(callback)
        
    def add_on_mouse_down_callback(self, button: int, callback: Callable[[Tuple[int, int]], None]) -> None:
        """添加鼠标按下回调"""
        if button not in self.on_mouse_down_callbacks:
            self.on_mouse_down_callbacks[button] = []
        self.on_mouse_down_callbacks[button].append(callback)
        
    def add_on_mouse_up_callback(self, button: int, callback: Callable[[Tuple[int, int]], None]) -> None:
        """添加鼠标释放回调"""
        if button not in self.on_mouse_up_callbacks:
            self.on_mouse_up_callbacks[button] = []
        self.on_mouse_up_callbacks[button].append(callback)
        
    def define_axis(self, name: str, positive_key: int, negative_key: int, 
                  sensitivity: float = 1.0) -> None:
        """定义输入轴（例如水平移动、垂直移动）"""
        if name not in self.axis_mappings:
            self.axis_mappings[name] = []
        self.axis_mappings[name].append((positive_key, negative_key, sensitivity))
        
    def get_axis(self, name: str) -> float:
        """获取输入轴的值（范围-1到1）"""
        if name not in self.axis_mappings:
            return 0.0
            
        value = 0.0
        for mapping in self.axis_mappings[name]:
            positive_key, negative_key, sensitivity = mapping
            if self.is_key_pressed(positive_key):
                value += sensitivity
            if self.is_key_pressed(negative_key):
                value -= sensitivity
                
        # 限制范围到[-1, 1]
        return max(-1.0, min(1.0, value))
