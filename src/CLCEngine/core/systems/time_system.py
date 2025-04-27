import time
from typing import Optional

class TimeSystem:
    """
    时间系统，管理游戏时间和帧率
    """
    _instance: Optional['TimeSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeSystem, cls).__new__(cls)
            cls._instance._init_singleton()
        return cls._instance
    
    def _init_singleton(self):
        """初始化单例"""
        self.start_time = time.time()
        self.current_time = self.start_time
        self.previous_time = self.start_time
        self.delta_time = 0.0
        self.fixed_delta_time = 0.02  # 固定时间步长，默认50FPS
        self.time_scale = 1.0  # 时间缩放
        self.frame_count = 0
        self.fps = 0
        self.fps_update_interval = 0.5  # 更新FPS的时间间隔
        self.last_fps_update_time = self.start_time
        self.frames_since_last_fps_update = 0
        self.max_delta_time = 0.1  # 最大帧时间，用于防止大延迟
        self.target_fps = 60  # 目标帧率
        self.vsync_enabled = True  # 是否启用垂直同步
        
    def update(self):
        """更新时间系统，每帧调用"""
        self.previous_time = self.current_time
        self.current_time = time.time()
        
        # 计算实际帧时间
        raw_delta_time = self.current_time - self.previous_time
        
        # 限制最大帧时间，避免大延迟导致物理错误
        clamped_delta_time = min(raw_delta_time, self.max_delta_time)
        
        # 应用时间缩放
        self.delta_time = clamped_delta_time * self.time_scale
        
        # 更新帧计数
        self.frame_count += 1
        self.frames_since_last_fps_update += 1
        
        # 更新FPS
        if self.current_time - self.last_fps_update_time >= self.fps_update_interval:
            elapsed = self.current_time - self.last_fps_update_time
            self.fps = self.frames_since_last_fps_update / elapsed
            self.last_fps_update_time = self.current_time
            self.frames_since_last_fps_update = 0
            
    def get_time(self) -> float:
        """获取从游戏开始到现在的总时间（秒）"""
        return self.current_time - self.start_time
        
    def get_delta_time(self) -> float:
        """获取上一帧到当前帧的时间间隔（秒）"""
        return self.delta_time
        
    def get_fixed_delta_time(self) -> float:
        """获取固定时间步长"""
        return self.fixed_delta_time
        
    def get_fps(self) -> float:
        """获取当前帧率"""
        return self.fps
        
    def get_frame_count(self) -> int:
        """获取总帧数"""
        return self.frame_count
        
    def set_time_scale(self, scale: float) -> None:
        """设置时间缩放"""
        self.time_scale = max(0.0, scale)
        
    def set_fixed_delta_time(self, fixed_delta_time: float) -> None:
        """设置固定时间步长"""
        self.fixed_delta_time = max(0.001, fixed_delta_time)
        
    def set_target_fps(self, fps: int) -> None:
        """设置目标帧率"""
        self.target_fps = max(1, fps)
        
    def set_vsync(self, enabled: bool) -> None:
        """设置是否启用垂直同步"""
        self.vsync_enabled = enabled
        
    def should_run_fixed_update(self) -> bool:
        """检查是否应该运行固定更新"""
        return self.get_time() % self.fixed_delta_time < self.delta_time
