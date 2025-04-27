# CLC Engine

CLC Engine是一个基于pygame的2D游戏引擎，专为上海科技大学SI100b课程设计。它采用GameObject-Component架构，提供了一个易于使用的编辑器界面，使新手能够快速构建和测试游戏。

## 主要特性

- **GameObject-Component架构**：使用现代游戏引擎设计理念，便于扩展和复用
- **编辑器模式**：直观的可视化编辑界面，无需编程即可创建游戏场景
- **事件系统**：灵活的发布-订阅事件系统，便于游戏对象间通信
- **输入系统**：统一的输入处理，支持键盘、鼠标和控制器
- **时间系统**：精确的时间控制，支持时间缩放和固定时间步长
- **碰撞系统**：内置碰撞检测，支持多种形状的碰撞器
- **场景管理**：场景创建、保存和加载

## 安装与依赖

### 依赖项

- Python 3.10+
- Pygame 2.0+
- Pygame_gui

### 安装

1. 克隆本仓库：
   ```
   git clone https://github.com/yourusername/clc-engine.git
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 快速开始

### 启动编辑器

```
python -m src.CLCEngine --editor
```

### 启动游戏（运行模式）

```
python -m src.CLCEngine
```

### 自定义窗口大小

```
python -m src.CLCEngine --size 1280x720
```

### 加载场景

```
python -m src.CLCEngine --scene path/to/scene.json
```

## 编辑器使用指南

1. **创建游戏对象**：点击层级窗口中的"创建"按钮
2. **添加组件**：在检查器窗口中点击"添加组件"，选择所需组件
3. **运行游戏**：点击工具栏上的"运行"按钮
4. **保存/加载场景**：点击工具栏上的"保存"或"加载"按钮

## 编程指南

### 创建自定义组件

```python
from CLCEngine.core.component import Component

class MyComponent(Component):
    def __init__(self, gameobject):
        super().__init__(gameobject)
        self.my_value = 0
        
    def update(self, delta_time):
        # 在每帧更新时执行的代码
        self.my_value += delta_time
        
    def fixed_update(self, fixed_delta_time):
        # 在固定时间间隔更新时执行的代码
        pass
```

### 创建和使用游戏对象

```python
from CLCEngine.core.scene import Scene
from CLCEngine.core.gameobject import GameObject
from CLCEngine.core.build_in_components.transform import Transform

# 创建场景
scene = Scene("My Scene")

# 创建游戏对象
player = scene.create_gameobject("Player")

# 获取变换组件
transform = player.get_component(Transform)
transform.set_position(100, 100)

# 添加自定义组件
player.add_component(MyComponent)
```

## 贡献

欢迎对本项目进行贡献！请先fork本仓库，然后提交pull request。

## 许可

本项目采用MIT许可证。

## 联系方式

如有问题，请联系：your.email@example.com

