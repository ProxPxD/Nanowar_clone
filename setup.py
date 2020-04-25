import sys
from cx_Freeze import setup, Executable

build_exe_options = {"packages": ["pygame", "gameplay", "time"],
                     "include_files": [
                         "__pycache__", 
                         "data",
                         "levels", 
                         "music",
                         "pictures", 
                         "Button.py",
                         "CellEnemy.py",
                         "Cell.py",
                         "gameplay.py",
                         "Level.py",
                         "Menu.py"
                         ]}

base = None
base = "win32gui"

setup(name = "nanowar",
      version = "1.0",
      description = "My game: nanowar",
      options = {"build_exe": build_exe_options},
      executables = [Executable("nanowar.py", base = base)] )
