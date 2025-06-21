import os
import platform
from pathlib import Path

# Default mind folder
if platform.system() == "Windows":
    user_profile = Path.home()
else:
    user_profile = Path.home()
_default_mind_folder = Path(user_profile) / ".guardin_mind"
_default_minders_folder = (_default_mind_folder / "minders") # Folder for minders installation
_default_minders_folder.mkdir(parents=True, exist_ok=True)

# To string
_default_mind_folder = str(_default_mind_folder)
_default_minders_folder = str(_default_minders_folder)
