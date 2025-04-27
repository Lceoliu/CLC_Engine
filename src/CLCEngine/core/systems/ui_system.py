import pygame
import pygame_gui
import os
from core.settings.defaults import *
from pygame_gui.core import ObjectID 
from typing import Dict, List, Any, Optional, Callable, Tuple, Literal

from .input_system import InputSystem
from ..systems.event_system import Event, EventArgs

class UIEventArgs(EventArgs):
    """UI事件参数"""
    def __init__(self, ui_element: Any, ui_id: str = ""):
        self.ui_element = ui_element
        self.ui_id = ui_id

class UISelectionEventArgs(UIEventArgs):
    """UI选择事件参数"""
    def __init__(self, ui_element: Any, ui_id: str, selection: str):
        super().__init__(ui_element, ui_id)
        self.selection = selection

class UIValueEventArgs(UIEventArgs):
    """UI值改变事件参数"""
    def __init__(self, ui_element: Any, ui_id: str, value: Any):
        super().__init__(ui_element, ui_id)
        self.value = value

class UILayoutElement(pygame_gui.core.UIContainer):
    """UI布局类，用于管理UI元素的布局和位置"""
    def __init__(self, 
                 relative_rect = pygame.Rect(0, 0, -1, -1), 
                 manager : Optional[pygame_gui.UIManager] = None, 
                 parent : Optional[pygame_gui.core.UIElement] = None,
                 container : Optional[pygame_gui.core.UIContainer] = None,
                 expand_with : Optional[Literal["width", "height", "fit"]] = None,
                 **kwargs):
        anchors = {}
        if expand_with is not None:
            if expand_with == "width":
                anchors["left"] = "left"
                anchors["right"] = "right"
            elif expand_with == "height":
                anchors["top"] = "top"
                anchors["bottom"] = "bottom"
            elif expand_with == "fit":
                anchors["left"] = "left"
                anchors["right"] = "right"
                anchors["top"] = "top"
                anchors["bottom"] = "bottom"
        super().__init__(relative_rect = relative_rect,
                         manager=manager,
                         container=container,
                         parent_element=parent,
                         anchors=anchors,
                         object_id=kwargs.get("object_id", ObjectID(object_id="#layout_element", class_id="@layout")))

    def __enter__(self):
        UISystem._parent_stack.append(self)
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if UISystem._parent_stack and UISystem._parent_stack[-1] == self:
            UISystem._parent_stack.pop()
        return False

class HorizontalLayout(UILayoutElement):
    """水平布局类"""
    def __init__(self,
                 relative_rect = pygame.Rect(0, 0, -1, -1),
                 manager : Optional[pygame_gui.UIManager] = None,
                 parent : Optional[pygame_gui.core.UIElement] = None,
                 container : Optional[pygame_gui.core.UIContainer] = None,
                 spacing: int = 10,
                 expand_with : Optional[Literal["width", "height", "fit"]] = "width"):
       
        super().__init__(relative_rect = relative_rect,
                         manager=manager,
                         container=container,
                         parent=parent,
                         expand_with=expand_with,)
        self.spacing = 10  # 子元素之间的间距

class VerticalLayout(UILayoutElement):
    """垂直布局类"""
    def __init__(self, 
                 relative_rect = pygame.Rect(0, 0, -1, -1),
                 manager : Optional[pygame_gui.UIManager] = None,
                 parent : Optional[pygame_gui.core.UIElement] = None,
                 container : Optional[pygame_gui.core.UIContainer] = None,
                 spacing: int = 10,
                 expand_with : Optional[Literal["width", "height", "fit"]] = "height"):
        super().__init__(relative_rect = relative_rect,
                         manager=manager,
                         container=container,
                         parent=parent,
                         expand_with=expand_with,)
        self.spacing = 10  # 子元素之间的间距

class UISystem:
    """
    UI系统，用于创建和管理游戏中的用户界面
    支持通用UI元素以及编辑器界面
    """
    _instance: Optional['UISystem'] = None
    _parent_stack: List[Optional[pygame_gui.core.UIContainer]] = []  # 用于存储父容器的栈
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UISystem, cls).__new__(cls)
            cls._instance._init_singleton()
            cls._parent_stack = []
        return cls._instance
    
    def _init_singleton(self):
        """初始化单例"""
        self.manager = None
        self.screen_size = (800, 600)
        self.theme_path = None
        
        # UI元素字典，通过ID引用
        self.elements: Dict[str, pygame_gui.core.UIElement] = {}
        
        # UI元素组，用于组织UI元素
        self.groups: Dict[str, Dict[str, pygame_gui.core.UIElement]] = {}
        
        # 事件系统
        self.on_button_clicked = Event[UIEventArgs]("ui_button_clicked")
        self.on_dropdown_selected = Event[UISelectionEventArgs]("ui_dropdown_selected")
        self.on_selection_list_changed = Event[UISelectionEventArgs]("ui_selection_list_changed")
        self.on_text_entry_changed = Event[UIValueEventArgs]("ui_text_entry_changed")
        self.on_slider_moved = Event[UIValueEventArgs]("ui_slider_moved")
        
    def initialize(self, screen_size: Tuple[int, int], theme_path: str = None):
        """初始化UI系统"""
        self.screen_size = screen_size
        self.theme_path = theme_path
        self.manager = pygame_gui.UIManager(screen_size,
                                            theme_path=theme_path,
                                            starting_language='zh')
       
    def update(self, delta_time: float):
        """更新UI系统"""
        if self.manager is None:
            return
            
        self.manager.update(delta_time)
    
    def set_theme(self, theme_path: str):
        """设置UI主题"""
        if self.manager is None:
            return
                
        try:    
            self.manager.set_theme(theme_path)
            self.theme_path = theme_path            
        except FileNotFoundError:
            print(f"主题文件 {theme_path} 未找到。请检查路径是否正确。")
        except Exception as e:
            print(f"设置主题时发生错误: {e}")
    
    def _refresh_ui(self):
        """刷新UI元素"""
        if self.manager is None:
            return
            
        for element in self.elements.values():
            element.rebuild()
    
    def process_events(self, event: pygame.event.Event):
        """处理UI事件"""
        if self.manager is None:
            return
            
        self.manager.process_events(event)
        
        # 处理pygame_gui生成的事件
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for element_id, element in self.elements.items():
                if event.ui_element == element:
                    self.on_button_clicked.invoke(self, UIEventArgs(element, element_id))
                    
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            for element_id, element in self.elements.items():
                if event.ui_element == element:
                    self.on_dropdown_selected.invoke(self, UISelectionEventArgs(element, element_id, event.text))
                    
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            for element_id, element in self.elements.items():
                if event.ui_element == element:
                    self.on_selection_list_changed.invoke(self, UISelectionEventArgs(element, element_id, event.text))
                    
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            for element_id, element in self.elements.items():
                if event.ui_element == element:
                    self.on_text_entry_changed.invoke(self, UIValueEventArgs(element, element_id, event.text))
                    
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            for element_id, element in self.elements.items():
                if event.ui_element == element:
                    self.on_slider_moved.invoke(self, UIValueEventArgs(element, element_id, event.value))
        
    def draw(self, screen: pygame.Surface):
        """绘制UI"""
        if self.manager is None:
            return
            
        self.manager.draw_ui(screen)
        
    def clear(self):
        """清除所有UI元素"""
        if self.manager is None:
            return
            
        self.manager.clear_and_reset()
        self.elements.clear()
        self.groups.clear()
        
    def create_element(self, element_type: str, element_id: str, rect: pygame.Rect, 
                      container: Optional[pygame_gui.core.UIContainer] = None, 
                      **kwargs) -> Optional[pygame_gui.core.UIElement]:
        """
        创建UI元素
        
        Args:
            element_type: 元素类型，如'button', 'label', 'text_entry'等
            element_id: 元素ID，用于引用
            rect: 元素矩形区域
            container: 容器，如果为None则添加到根容器
            **kwargs: 其他参数，如text, starting_height等
            
        Returns:
            创建的UI元素
        """
        if self.manager is None:
            return None
            
        element = None
        if element_type == "horizontal_layout":
            element = HorizontalLayout(relative_rect=rect, manager=self.manager, container=container, **kwargs)
        elif element_type == "vertical_layout":
            element = VerticalLayout(relative_rect=rect, manager=self.manager, container=container, **kwargs)
        elif element_type == 'button':
            element = pygame_gui.elements.UIButton(
                relative_rect=rect,
                text=kwargs.get('text', ''),
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'label':
            element = pygame_gui.elements.UILabel(
                relative_rect=rect,
                text=kwargs.get('text', ''),
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'text_entry':
            element = pygame_gui.elements.UITextEntryLine(
                relative_rect=rect,
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
            if 'text' in kwargs:
                element.set_text(kwargs['text'])
        elif element_type == 'dropdown':
            element = pygame_gui.elements.UIDropDownMenu(
                options_list=kwargs.get('options', []),
                starting_option=kwargs.get('starting_option', None),
                relative_rect=rect,
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'selection_list':
            element = pygame_gui.elements.UISelectionList(
                relative_rect=rect,
                item_list=kwargs.get('items', []),
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'slider':
            element = pygame_gui.elements.UIHorizontalSlider(
                relative_rect=rect,
                start_value=kwargs.get('start_value', 0),
                value_range=kwargs.get('value_range', (0, 100)),
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'panel':
            element = pygame_gui.elements.UIPanel(
                relative_rect=rect,
                manager=self.manager,
                starting_layer_height=kwargs.get('starting_height', 1),
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'window':
            element = pygame_gui.elements.UIWindow(
                rect=rect,
                manager=self.manager,
                window_display_title=kwargs.get('title', ''),
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'text_box':
            element = pygame_gui.elements.UITextBox(
                html_text=kwargs.get('text', ''),
                relative_rect=rect,
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
        elif element_type == 'image':
            element = pygame_gui.elements.UIImage(
                relative_rect=rect,
                image_surface=kwargs.get('image', None),
                manager=self.manager,
                container=container,
                object_id=kwargs.get('object_id', None)
            )
            
        if element is not None:
            self.elements[element_id] = element
            
            # 如果有组名，添加到组中
            group_name = kwargs.get('group', None)
            if group_name:
                if group_name not in self.groups:
                    self.groups[group_name] = {}
                self.groups[group_name][element_id] = element
                
        return element
        
    def get_element(self, element_id: str) -> Optional[pygame_gui.core.UIElement]:
        """
        获取UI元素
        
        Args:
            element_id: 元素ID
            
        Returns:
            UI元素
        """
        return self.elements.get(element_id)
        
    def set_element_text(self, element_id: str, text: str) -> bool:
        """
        设置UI元素文本
        
        Args:
            element_id: 元素ID
            text: 文本
            
        Returns:
            是否成功
        """
        element = self.get_element(element_id)
        if element is None:
            return False
            
        if hasattr(element, 'set_text'):
            element.set_text(text)
            return True
        elif isinstance(element, pygame_gui.elements.UITextBox):
            element.html_text = text
            element.rebuild()
            return True
            
        return False
        
    def get_element_text(self, element_id: str) -> Optional[str]:
        """
        获取UI元素文本
        
        Args:
            element_id: 元素ID
            
        Returns:
            文本
        """
        element = self.get_element(element_id)
        if element is None:
            return None
            
        if hasattr(element, 'get_text'):
            return element.get_text()
        elif isinstance(element, pygame_gui.elements.UITextBox):
            return element.html_text
            
        return None
        
    def remove_element(self, element_id: str) -> bool:
        """
        移除UI元素
        
        Args:
            element_id: 元素ID
            
        Returns:
            是否成功
        """
        element = self.get_element(element_id)
        if element is None:
            return False
            
        element.kill()
        self.elements.pop(element_id)
        
        # 从所有组中移除
        for group in self.groups.values():
            if element_id in group:
                group.pop(element_id)
                
        return True
        
    def create_group(self, group_id: str, elements: Dict[str, Dict[str, Any]]) -> Dict[str, pygame_gui.core.UIElement]:
        """
        创建UI元素组
        
        Args:
            group_id: 组ID
            elements: 元素定义字典，格式为{元素ID: {type: 类型, rect: 矩形, ...}}
            
        Returns:
            创建的UI元素字典
        """
        self.groups[group_id] = {}
        
        for element_id, element_def in elements.items():
            element_type = element_def.pop('type')
            rect = element_def.pop('rect')
            element_def['group'] = group_id
            
            element = self.create_element(element_type, element_id, rect, **element_def)
            if element:
                self.groups[group_id][element_id] = element
                
        return self.groups[group_id]
        
    def hide_group(self, group_id: str) -> bool:
        """
        隐藏UI元素组
        
        Args:
            group_id: 组ID
            
        Returns:
            是否成功
        """
        if group_id not in self.groups:
            return False
            
        for element in self.groups[group_id].values():
            element.hide()
            
        return True
        
    def show_group(self, group_id: str) -> bool:
        """
        显示UI元素组
        
        Args:
            group_id: 组ID
            
        Returns:
            是否成功
        """
        if group_id not in self.groups:
            return False
            
        for element in self.groups[group_id].values():
            element.show()
            
        return True
        
    def remove_group(self, group_id: str) -> bool:
        """
        移除UI元素组
        
        Args:
            group_id: 组ID
            
        Returns:
            是否成功
        """
        if group_id not in self.groups:
            return False
            
        for element_id in list(self.groups[group_id].keys()):
            self.remove_element(element_id)
            
        self.groups.pop(group_id)
        return True
        
    # 以下是一些常用的UI创建函数
    def create_hr(self, rect: pygame.Rect, **kwargs) -> Optional[HorizontalLayout]:
        """
        创建水平布局
        
        Args:
            rect: 矩形区域
            **kwargs: 其他参数
            
        Returns:
            水平布局
        """
        parent = UISystem._parent_stack[-1] if UISystem._parent_stack else None
        layout = HorizontalLayout(parent)
        container = pygame_gui.core.UIContainer()
        return layout
    
    def create_button(self, element_id: str, text: str, rect: pygame.Rect, 
                     container: Optional[pygame_gui.core.UIContainer] = None,
                     **kwargs) -> Optional[pygame_gui.elements.UIButton]:
        """
        创建按钮
        
        Args:
            element_id: 元素ID
            text: 按钮文本
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            按钮
        """
        kwargs['text'] = text
        return self.create_element('button', element_id, rect, container, **kwargs)
        
    def create_label(self, element_id: str, text: str, rect: pygame.Rect,
                    container: Optional[pygame_gui.core.UIContainer] = None,
                    **kwargs) -> Optional[pygame_gui.elements.UILabel]:
        """
        创建标签
        
        Args:
            element_id: 元素ID
            text: 标签文本
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            标签
        """
        kwargs['text'] = text
        return self.create_element('label', element_id, rect, container, **kwargs)
        
    def create_text_entry(self, element_id: str, initial_text: str, rect: pygame.Rect,
                         container: Optional[pygame_gui.core.UIContainer] = None,
                         **kwargs) -> Optional[pygame_gui.elements.UITextEntryLine]:
        """
        创建文本输入框
        
        Args:
            element_id: 元素ID
            initial_text: 初始文本
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            文本输入框
        """
        kwargs['text'] = initial_text
        return self.create_element('text_entry', element_id, rect, container, **kwargs)
        
    def create_dropdown(self, element_id: str, options: List[str], starting_option: str,
                       rect: pygame.Rect, container: Optional[pygame_gui.core.UIContainer] = None,
                       **kwargs) -> Optional[pygame_gui.elements.UIDropDownMenu]:
        """
        创建下拉菜单
        
        Args:
            element_id: 元素ID
            options: 选项列表
            starting_option: 初始选项
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            下拉菜单
        """
        kwargs['options'] = options
        kwargs['starting_option'] = starting_option
        return self.create_element('dropdown', element_id, rect, container, **kwargs)
        
    def create_selection_list(self, element_id: str, items: List[str], rect: pygame.Rect,
                            container: Optional[pygame_gui.core.UIContainer] = None,
                            **kwargs) -> Optional[pygame_gui.elements.UISelectionList]:
        """
        创建选择列表
        
        Args:
            element_id: 元素ID
            items: 项目列表
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            选择列表
        """
        kwargs['items'] = items
        return self.create_element('selection_list', element_id, rect, container, **kwargs)
        
    def create_slider(self, element_id: str, start_value: float, value_range: Tuple[float, float],
                     rect: pygame.Rect, container: Optional[pygame_gui.core.UIContainer] = None,
                     **kwargs) -> Optional[pygame_gui.elements.UIHorizontalSlider]:
        """
        创建滑块
        
        Args:
            element_id: 元素ID
            start_value: 初始值
            value_range: 值范围
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            滑块
        """
        kwargs['start_value'] = start_value
        kwargs['value_range'] = value_range
        return self.create_element('slider', element_id, rect, container, **kwargs)
        
    def create_panel(self, element_id: str, rect: pygame.Rect,
                    container: Optional[pygame_gui.core.UIContainer] = None,
                    **kwargs) -> Optional[pygame_gui.elements.UIPanel]:
        """
        创建面板
        
        Args:
            element_id: 元素ID
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            面板
        """
        return self.create_element('panel', element_id, rect, container, **kwargs)
        
    def create_window(self, element_id: str, title: str, rect: pygame.Rect,
                     **kwargs) -> Optional[pygame_gui.elements.UIWindow]:
        """
        创建窗口
        
        Args:
            element_id: 元素ID
            title: 窗口标题
            rect: 矩形区域
            **kwargs: 其他参数
            
        Returns:
            窗口
        """
        kwargs['title'] = title
        return self.create_element('window', element_id, rect, None, **kwargs)
        
    def create_text_box(self, element_id: str, text: str, rect: pygame.Rect,
                       container: Optional[pygame_gui.core.UIContainer] = None,
                       **kwargs) -> Optional[pygame_gui.elements.UITextBox]:
        """
        创建文本框
        
        Args:
            element_id: 元素ID
            text: 文本
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            文本框
        """
        kwargs['text'] = text
        return self.create_element('text_box', element_id, rect, container, **kwargs)
        
    def create_image(self, element_id: str, image: pygame.Surface, rect: pygame.Rect,
                    container: Optional[pygame_gui.core.UIContainer] = None,
                    **kwargs) -> Optional[pygame_gui.elements.UIImage]:
        """
        创建图像
        
        Args:
            element_id: 元素ID
            image: 图像
            rect: 矩形区域
            container: 容器
            **kwargs: 其他参数
            
        Returns:
            图像
        """
        kwargs['image'] = image
        return self.create_element('image', element_id, rect, container, **kwargs)

    def create_editor_ui(self):
        """
        创建编辑器UI
        """
        if self.manager is None:
            return
        if hasattr(self, 'editor_ui_window'):
            self.editor_ui_window.kill()
        self.editor_ui_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((0, 0), self.screen_size),
            manager=self.manager,
            window_display_title="",
            object_id=ObjectID(object_id="#editor_ui_window", class_id="@transparent_window")
        )
        self.create_button("editor_save_button", "保存", pygame.Rect((10, 10), (100, 30)), self.editor_ui_window)