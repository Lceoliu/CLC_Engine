import os
import json
import pygame
from typing import Dict, List, Any, Optional, Tuple, Union, Set
import pathlib
from core.systems.event_system import Event, EventArgs

class AssetLoadedEventArgs(EventArgs):
    """资源加载事件参数"""
    def __init__(self, asset_id: str, asset_type: str, asset: Any):
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.asset = asset

class AssetAddressSystem:
    """
    资源寻址系统，用于管理和加载游戏资源
    支持多种资源类型，如图像、音频、字体等
    
    作为Python库，支持用户指定自己的资源路径
    """
    _instance: Optional['AssetAddressSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssetAddressSystem, cls).__new__(cls)
            cls._instance._init_singleton()
        return cls._instance
    
    def _init_singleton(self):
        """初始化单例"""
        # 资源路径映射，key: asset_id, value: (asset_type, path)
        self._asset_paths: Dict[str, Tuple[str, str]] = {}
        
        # 已加载的资源，key: asset_id, value: asset
        self._loaded_assets: Dict[str, Any] = {}
        
        # 用户资源根目录
        self._user_asset_roots: List[str] = []
        
        # 资源类型
        self.ASSET_TYPE_IMAGE = "image"
        self.ASSET_TYPE_SOUND = "sound"
        self.ASSET_TYPE_FONT = "font"
        self.ASSET_TYPE_JSON = "json"
        self.ASSET_TYPE_TEXT = "text"
        
        # 资源扩展名到类型映射
        self._ext_to_type = {
            ".png": self.ASSET_TYPE_IMAGE,
            ".jpg": self.ASSET_TYPE_IMAGE,
            ".jpeg": self.ASSET_TYPE_IMAGE,
            ".bmp": self.ASSET_TYPE_IMAGE,
            ".gif": self.ASSET_TYPE_IMAGE,
            
            ".wav": self.ASSET_TYPE_SOUND,
            ".mp3": self.ASSET_TYPE_SOUND,
            ".ogg": self.ASSET_TYPE_SOUND,
            
            ".ttf": self.ASSET_TYPE_FONT,
            ".otf": self.ASSET_TYPE_FONT,
            
            ".json": self.ASSET_TYPE_JSON,
            
            ".txt": self.ASSET_TYPE_TEXT,
        }
        
        # 事件
        self.on_asset_loaded = Event[AssetLoadedEventArgs]("asset_loaded")
        
    def add_user_asset_root(self, path: str) -> bool:
        """
        添加用户资源根目录
        
        Args:
            path: 目录路径
            
        Returns:
            是否成功添加
        """
        if not os.path.isdir(path):
            return False
            
        absolute_path = os.path.abspath(path)
        if absolute_path not in self._user_asset_roots:
            self._user_asset_roots.append(absolute_path)
            return True
            
        return False
        
    def remove_user_asset_root(self, path: str) -> bool:
        """
        移除用户资源根目录
        
        Args:
            path: 目录路径
            
        Returns:
            是否成功移除
        """
        absolute_path = os.path.abspath(path)
        if absolute_path in self._user_asset_roots:
            self._user_asset_roots.remove(absolute_path)
            return True
            
        return False
        
    def register_asset(self, asset_id: str, asset_path: str, asset_type: Optional[str] = None) -> bool:
        """
        注册资源
        
        Args:
            asset_id: 资源ID
            asset_path: 资源路径，可以是相对于用户资源根目录的路径，也可以是绝对路径
            asset_type: 资源类型，如果为None则根据扩展名自动判断
            
        Returns:
            是否成功注册
        """
        # 检查路径是否存在
        full_path = self._find_asset_path(asset_path)
        if not full_path:
            return False
            
        # 如果没有指定资源类型，根据扩展名判断
        if asset_type is None:
            ext = os.path.splitext(asset_path)[1].lower()
            asset_type = self._ext_to_type.get(ext)
            if asset_type is None:
                return False
                
        # 注册资源
        self._asset_paths[asset_id] = (asset_type, full_path)
        return True
        
    def unregister_asset(self, asset_id: str) -> bool:
        """
        取消注册资源
        
        Args:
            asset_id: 资源ID
            
        Returns:
            是否成功取消注册
        """
        if asset_id in self._asset_paths:
            del self._asset_paths[asset_id]
            if asset_id in self._loaded_assets:
                del self._loaded_assets[asset_id]
            return True
            
        return False
        
    def load_asset(self, asset_id: str, force_reload: bool = False) -> Optional[Any]:
        """
        加载资源
        
        Args:
            asset_id: 资源ID
            force_reload: 是否强制重新加载
            
        Returns:
            加载的资源，加载失败返回None
        """
        # 检查资源是否已加载
        if not force_reload and asset_id in self._loaded_assets:
            return self._loaded_assets[asset_id]
            
        # 检查资源是否已注册
        if asset_id not in self._asset_paths:
            return None
            
        asset_type, asset_path = self._asset_paths[asset_id]
        asset = None
        
        try:
            # 根据资源类型加载
            if asset_type == self.ASSET_TYPE_IMAGE:
                asset = pygame.image.load(asset_path).convert_alpha()
            elif asset_type == self.ASSET_TYPE_SOUND:
                asset = pygame.mixer.Sound(asset_path)
            elif asset_type == self.ASSET_TYPE_FONT:
                # 假设font_size已经被设置或传入
                font_size = 24  # 默认大小
                asset = pygame.font.Font(asset_path, font_size)
            elif asset_type == self.ASSET_TYPE_JSON:
                with open(asset_path, 'r', encoding='utf-8') as f:
                    asset = json.load(f)
            elif asset_type == self.ASSET_TYPE_TEXT:
                with open(asset_path, 'r', encoding='utf-8') as f:
                    asset = f.read()
        except Exception as e:
            print(f"加载资源失败 {asset_id}: {e}")
            return None
            
        # 存储已加载的资源
        if asset is not None:
            self._loaded_assets[asset_id] = asset
            # 触发事件
            args = AssetLoadedEventArgs(asset_id, asset_type, asset)
            self.on_asset_loaded.invoke(self, args)
            
        return asset
        
    def load_font(self, asset_id: str, font_size: int) -> Optional[pygame.font.Font]:
        """
        加载字体
        
        Args:
            asset_id: 资源ID
            font_size: 字体大小
            
        Returns:
            加载的字体，加载失败返回None
        """
        # 检查资源是否已注册
        if asset_id not in self._asset_paths:
            return None
            
        asset_type, asset_path = self._asset_paths[asset_id]
        if asset_type != self.ASSET_TYPE_FONT:
            return None
            
        try:
            font = pygame.font.Font(asset_path, font_size)
            return font
        except Exception as e:
            print(f"加载字体失败 {asset_id}: {e}")
            return None
            
    def get_asset(self, asset_id: str) -> Optional[Any]:
        """
        获取已加载的资源
        
        Args:
            asset_id: 资源ID
            
        Returns:
            资源，如果未加载则返回None
        """
        return self._loaded_assets.get(asset_id)
        
    def is_asset_loaded(self, asset_id: str) -> bool:
        """
        检查资源是否已加载
        
        Args:
            asset_id: 资源ID
            
        Returns:
            是否已加载
        """
        return asset_id in self._loaded_assets
        
    def clear_assets(self) -> None:
        """
        清除所有已加载的资源
        """
        self._loaded_assets.clear()
        
    def scan_directory(self, directory: str, recursive: bool = True) -> Dict[str, Tuple[str, str]]:
        """
        扫描目录，自动注册资源
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描子目录
            
        Returns:
            注册的资源字典，key: asset_id, value: (asset_type, path)
        """
        registered_assets = {}
        
        full_path = self._find_asset_path(directory)
        if not full_path or not os.path.isdir(full_path):
            return registered_assets
            
        for path, dirs, files in os.walk(full_path):
            if not recursive and path != full_path:
                continue
                
            for file in files:
                file_path = os.path.join(path, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext not in self._ext_to_type:
                    continue
                    
                # 生成资源ID，相对于根目录的路径
                rel_path = os.path.relpath(file_path, full_path)
                asset_id = rel_path.replace('\\', '/')
                
                # 注册资源
                asset_type = self._ext_to_type[file_ext]
                self._asset_paths[asset_id] = (asset_type, file_path)
                registered_assets[asset_id] = (asset_type, file_path)
                
        return registered_assets
        
    def load_manifest(self, manifest_path: str) -> bool:
        """
        从资源清单文件加载资源
        
        Args:
            manifest_path: 清单文件路径
            
        Returns:
            是否成功加载
        """
        full_path = self._find_asset_path(manifest_path)
        if not full_path:
            return False
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                
            if not isinstance(manifest, dict):
                return False
                
            # 处理资源根目录
            if "asset_roots" in manifest and isinstance(manifest["asset_roots"], list):
                for root in manifest["asset_roots"]:
                    if isinstance(root, str):
                        # 解析路径，支持相对于清单文件的路径
                        manifest_dir = os.path.dirname(full_path)
                        root_path = os.path.normpath(os.path.join(manifest_dir, root))
                        self.add_user_asset_root(root_path)
                        
            # 处理资源
            if "assets" in manifest and isinstance(manifest["assets"], list):
                for asset in manifest["assets"]:
                    if not isinstance(asset, dict):
                        continue
                        
                    asset_id = asset.get("id")
                    asset_path = asset.get("path")
                    asset_type = asset.get("type")
                    
                    if asset_id and asset_path:
                        self.register_asset(asset_id, asset_path, asset_type)
                        
            return True
        except Exception as e:
            print(f"加载资源清单失败: {e}")
            return False
            
    def save_manifest(self, manifest_path: str) -> bool:
        """
        保存资源清单文件
        
        Args:
            manifest_path: 清单文件路径
            
        Returns:
            是否成功保存
        """
        try:
            manifest = {
                "asset_roots": self._user_asset_roots,
                "assets": []
            }
            
            for asset_id, (asset_type, asset_path) in self._asset_paths.items():
                manifest["assets"].append({
                    "id": asset_id,
                    "path": asset_path,
                    "type": asset_type
                })
                
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4)
                
            return True
        except Exception as e:
            print(f"保存资源清单失败: {e}")
            return False
            
    def _find_asset_path(self, asset_path: str) -> Optional[str]:
        """
        查找资源的完整路径
        
        Args:
            asset_path: 资源路径
            
        Returns:
            完整路径，未找到返回None
        """
        # 如果是绝对路径且存在，直接返回
        if os.path.isabs(asset_path) and os.path.exists(asset_path):
            return asset_path
            
        # 解析路径，处理跨平台问题
        path_obj = pathlib.Path(asset_path)
        # 在所有资源根目录中查找
        for root in self._user_asset_roots:
            full_path = os.path.join(root, path_obj.as_posix())
            if os.path.exists(full_path):
                return full_path
                
        return None
        
    def resize_image(self, asset_id: str, size: Tuple[int, int]) -> Optional[pygame.Surface]:
        """
        调整图像大小
        
        Args:
            asset_id: 资源ID
            size: 新的大小
            
        Returns:
            调整大小后的图像，失败返回None
        """
        image = self.get_asset(asset_id)
        if image is None or not isinstance(image, pygame.Surface):
            return None
            
        try:
            resized = pygame.transform.scale(image, size)
            return resized
        except Exception as e:
            print(f"调整图像大小失败 {asset_id}: {e}")
            return None
            
    def get_asset_info(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """
        获取资源信息
        
        Args:
            asset_id: 资源ID
            
        Returns:
            资源信息字典
        """
        if asset_id not in self._asset_paths:
            return None
            
        asset_type, asset_path = self._asset_paths[asset_id]
        info = {
            "id": asset_id,
            "type": asset_type,
            "path": asset_path,
            "loaded": asset_id in self._loaded_assets
        }
        
        return info
        
    def list_assets(self, asset_type: Optional[str] = None) -> List[str]:
        """
        列出所有资源ID
        
        Args:
            asset_type: 可选的资源类型过滤
            
        Returns:
            资源ID列表
        """
        if asset_type is None:
            return list(self._asset_paths.keys())
        else:
            return [asset_id for asset_id, (type_name, _) in self._asset_paths.items() 
                   if type_name == asset_type]
                   
    def get_asset_types(self) -> Set[str]:
        """
        获取所有已注册的资源类型
        
        Returns:
            资源类型集合
        """
        return {asset_type for _, (asset_type, _) in self._asset_paths.items()}
