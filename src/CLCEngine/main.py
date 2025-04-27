import sys
import time
import os

ENGINE_PATH = os.path.abspath(os.path.dirname(__file__))
if ENGINE_PATH not in sys.path:
    sys.path.append(ENGINE_PATH)
    
import pygame
import argparse
from core.settings import defaults

from typing import List, Tuple, Dict, Any, Optional

from core.scene import Scene
from core.gameobject import GameObject
from core.systems.time_system import TimeSystem
from core.systems.input_system import InputSystem
from core.systems.ui_system import UISystem, UIEventArgs, UIValueEventArgs, UISelectionEventArgs
from core.systems.event_system import EventSystem, Event, EventArgs
from utils.assets_adresser import AssetAddressSystem


class EngineEventArgs(EventArgs):
    """引擎事件参数基类"""
    pass


class ToggleEditorEventArgs(EngineEventArgs):
    """切换编辑器模式事件参数"""
    def __init__(self, is_editor_mode: bool):
        self.is_editor_mode = is_editor_mode


class TogglePauseEventArgs(EngineEventArgs):
    """切换暂停状态事件参数"""
    def __init__(self, is_paused: bool):
        self.is_paused = is_paused


class CLCEngine:
    """
    CLC游戏引擎主类
    """
    def __init__(self, 
                 screen_size: Tuple[int, int] = defaults.DefaultSettings.screen_size, 
                 title: str = "CLC Engine",
                 is_editor_mode: bool = defaults.DefaultSettings.is_editor_mode,):
        # 初始化pygame
        pygame.init()
        
        # 设置屏幕
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
        pygame.display.set_caption(title)
        
        # 初始化时间系统
        self.time_system = TimeSystem()
        
        # 初始化输入系统
        self.input_system = InputSystem()
        
        # 初始化UI系统
        self.ui_system = UISystem()
        self.ui_system.initialize(screen_size, theme_path=os.path.join(defaults.DefaultPath.editor_ui_themes_path, "default.json"))
        
        # 初始化事件系统
        self.event_system = EventSystem()
        
        # 初始化资源管理系统
        self.asset_system = AssetAddressSystem()
        
        # 场景管理
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        
        # 引擎状态
        self.is_running = False
        self.is_editor_mode = is_editor_mode
        if is_editor_mode:
            self.is_paused = True
            self.ui_system.create_editor_ui()
        else:
            self.is_paused = False
        
        # 引擎事件
        self.on_quit = Event[EventArgs]("engine:quit")
        self.on_toggle_editor = Event[ToggleEditorEventArgs]("engine:toggle_editor")
        self.on_toggle_pause = Event[TogglePauseEventArgs]("engine:toggle_pause")
        
        # 注册默认事件
        self._register_default_events()
        
    def _register_default_events(self):
        """注册默认事件处理器"""
        # 退出事件
        def on_quit(sender, args):
            self.is_running = False
        self.on_quit += on_quit
        
        # 切换编辑器模式事件
        def on_toggle_editor(sender, args):
            if isinstance(args, ToggleEditorEventArgs):
                self.set_editor_mode(args.is_editor_mode)
            else:
                self.set_editor_mode(not self.is_editor_mode)
        self.on_toggle_editor += on_toggle_editor
        
        # 暂停事件
        def on_toggle_pause(sender, args):
            if isinstance(args, TogglePauseEventArgs):
                self.is_paused = args.is_paused
            else:
                self.is_paused = not self.is_paused
        self.on_toggle_pause += on_toggle_pause
        
    def create_scene(self, name: str) -> Scene:
        """创建新场景"""
        scene = Scene(name, self.screen_size)
        self.scenes[name] = scene
        return scene
        
    def load_scene(self, name: str) -> Optional[Scene]:
        """加载已有场景"""
        if name in self.scenes:
            self.active_scene = self.scenes[name]
            if self.is_editor_mode:
                self.active_scene.set_editor_mode(True)
                self._refresh_editor_ui()
            return self.active_scene
        return None
        
    def load_scene_from_file(self, filepath: str) -> Optional[Scene]:
        """从文件加载场景"""
        try:
            scene = Scene.load(filepath)
            self.scenes[scene.name] = scene
            self.active_scene = scene
            if self.is_editor_mode:
                self.active_scene.set_editor_mode(True)
                self._refresh_editor_ui()
            return scene
        except Exception as e:
            print(f"加载场景失败: {e}")
            return None
            
    def set_editor_mode(self, enabled: bool):
        """设置编辑器模式"""
        self.is_editor_mode = enabled
        
        if self.active_scene:
            self.active_scene.set_editor_mode(enabled)
            
        if enabled:
            self.is_paused = True
            self._refresh_editor_ui()
            
    def _refresh_editor_ui(self):
        """刷新编辑器UI"""
        self.ui_system._refresh_ui()
        self._register_editor_callbacks()
        
    def _register_editor_callbacks(self):
        """注册编辑器UI回调"""
        # 播放按钮
        def on_play(sender, args):
            toggle_args = ToggleEditorEventArgs(False)
            self.on_toggle_editor.invoke(self, toggle_args)
        
        play_button = self.ui_system.get_element("play_button")
        if play_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_play
            
        # 暂停按钮
        def on_pause(sender, args):
            toggle_args = TogglePauseEventArgs(not self.is_paused)
            self.on_toggle_pause.invoke(self, toggle_args)
        
        pause_button = self.ui_system.get_element("pause_button")
        if pause_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_pause
        
        # 停止按钮
        def on_stop(sender, args):
            if not self.is_editor_mode:
                toggle_args = ToggleEditorEventArgs(True)
                self.on_toggle_editor.invoke(self, toggle_args)
            self.is_paused = False
        
        stop_button = self.ui_system.get_element("stop_button")
        if stop_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_stop
        
        # 保存按钮
        def on_save(sender, args):
            if self.active_scene:
                # TODO: 实现保存对话框
                self.active_scene.save(f"{self.active_scene.name}.json")
        
        save_button = self.ui_system.get_element("save_button")
        if save_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_save
        
        # 加载按钮
        def on_load(sender, args):
            # TODO: 实现加载对话框
            pass
        
        load_button = self.ui_system.get_element("load_button")
        if load_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_load
        
        # 创建对象按钮
        def on_create_object(sender, args):
            if self.active_scene:
                obj = self.active_scene.create_gameobject("New Object")
                # TODO: 刷新层级UI
        
        create_object_button = self.ui_system.get_element("create_object_button")
        if create_object_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_create_object
        
        # 删除对象按钮
        def on_delete_object(sender, args):
            # TODO: 实现选中对象的删除
            pass
        
        delete_object_button = self.ui_system.get_element("delete_object_button")
        if delete_object_button:
            button_event = self.ui_system.get_event("button_clicked")
            if button_event:
                button_event += on_delete_object
        
    def run(self):
        """运行游戏引擎主循环"""
        self.is_running = True
        
        # 如果没有活动场景，创建一个
        if not self.active_scene:
            self.active_scene = self.create_scene("Default Scene")
            
        # 设置编辑器模式
        self.set_editor_mode(self.is_editor_mode)
        
        # 初始化场景
        self.active_scene.start()
        
        # 主循环
        accumulated_time = 0
        fixed_delta_time = self.time_system.get_fixed_delta_time()
        events_list = []
        while self.is_running:
            # 更新时间系统
            self.time_system.update()
            delta_time = self.time_system.get_delta_time()
            
            events_list = pygame.event.get()
            # 处理输入
            self.input_system.update(events_list)
            
            # 检查退出事件
            for event in events_list:
                if event.type == pygame.QUIT:
                    self.on_quit.invoke(self, None)
                elif event.type == pygame.VIDEORESIZE:

                    self.screen_size = (event.w, event.h)
                    self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                    self.ui_system.initialize(self.screen_size)
                    if self.is_editor_mode:
                        self._refresh_editor_ui()
                
                # 处理UI事件
                self.ui_system.process_events(event)
            
            # 游戏逻辑更新（非暂停状态）
            if not self.is_paused or self.is_editor_mode:
                # 更新场景
                if self.active_scene:
                    self.active_scene.update(delta_time)
                    
                    # 固定时间步长更新（物理等）
                    accumulated_time += delta_time
                    while accumulated_time >= fixed_delta_time:
                        self.active_scene.fixed_update(fixed_delta_time)
                        accumulated_time -= fixed_delta_time
                
                # 更新UI系统
                self.ui_system.update(delta_time)
            
            # 渲染
            self.screen.fill((0, 0, 0))  # 清屏
            
            # 渲染场景
            if self.active_scene:
                self.active_scene.render(self.screen)
                
            # 渲染UI
            self.ui_system.draw(self.screen)
            
            # 更新显示
            pygame.display.flip()
            
            # 帧率控制
            if self.time_system.vsync_enabled:
                pygame.time.Clock().tick(self.time_system.target_fps)
                
        # 清理资源
        pygame.quit()

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="CLC Engine")
    parser.add_argument("--editor", action="store_true", help="启动编辑器模式")
    parser.add_argument("--scene", type=str, help="加载指定场景文件")
    parser.add_argument("--size", type=str, default="800x600", help="设置窗口大小，格式为'宽x高'")
    parser.add_argument("--assets", type=str, help="指定资源目录")
    parser.add_argument("--manifest", type=str, help="指定资源清单文件")
    
    args = parser.parse_args()
    
    # 解析窗口大小
    try:
        width, height = map(int, args.size.split('x'))
        screen_size = (width, height)
    except:
        print("窗口大小格式错误，使用默认值800x600")
        screen_size = (800, 600)
        
    return args, screen_size

def main():
    """引擎入口函数"""
    args, screen_size = parse_arguments()
    
    # 创建引擎实例
    engine = CLCEngine(screen_size, "CLC Engine")
    
    # 设置资源路径（如果指定）
    if args.assets:
        engine.asset_system.add_user_asset_root(args.assets)
        
    # 加载资源清单（如果指定）
    if args.manifest:
        engine.asset_system.load_manifest(args.manifest)
    
    # 设置模式
    engine.set_editor_mode(args.editor)
    
    # 加载场景（如果指定）
    if args.scene:
        engine.load_scene_from_file(args.scene)
        
    # 运行引擎
    engine.run()
    
if __name__ == "__main__":
    main()



