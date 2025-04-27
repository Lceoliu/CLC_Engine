import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.CLCEngine.utils import *


abs_path = get_root_path.ABS_ROOT_PATH
print(abs_path)