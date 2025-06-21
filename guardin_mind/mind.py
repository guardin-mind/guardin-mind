from colorama import init, Fore, Style # Use colorama for color prints
from guardin_mind.configs import _default_minders_folder
import os
import inspect
import importlib.util
import re
from typing import TypeVar, Type

init(autoreset=True) # Init colorama

T = TypeVar("T")

class MinderSearch:
    '''
    MinderSearch class responsible for searching minder modules locally.
    A "minder" is assumed to be a module or package managed by this system.
    '''

    def __init__(self, minders_dir: str | None = None):
        # If debug mode is enabled, log the key directories involved in the execution.
        self.minders_dir = minders_dir if minders_dir is not None else _default_minders_folder

    def search_minder_locally(self, minder_name: str) -> str | None:
        '''
        Searches for a minder directory matching the given name inside the local "minders" directory.
        This method performs a case-sensitive match and does not recurse into subdirectories.

        Args:
            minder_name (str): The exact name of the minder directory to find.

        Returns:
            str | None: The absolute path to the minder directory if found, otherwise None.
        '''
        minders_dir = os.path.join(self.minders_dir, "minders")

        # Iterate over entries in the "minders" directory
        for entry in os.listdir(minders_dir):
            full_path = os.path.join(minders_dir, entry)
            # Check if entry is a directory and matches the minder_name exactly (case-sensitive)
            if os.path.isdir(full_path) and entry == minder_name:
                # Return normalized absolute path with forward slashes for consistency
                return full_path.replace("\\", "/")

        # Return None if no matching minder directory found
        return None

    def load_minder(self, minder_path: str, minder_name: str) -> type | None:
        '''
        Dynamically loads a minder module from the given Python file path and retrieves the minder class by name.

        Args:
            minder_path (str): Absolute path to the minder's Python (.py) file.
            minder_name (str): Name of the minder class expected inside the module.

        Returns:
            type | None: The minder class if successfully loaded, None otherwise.
        '''
        try:
            # Extract module name from the file name (without extension)
            module_name = os.path.splitext(os.path.basename(minder_path))[0]

            # Create a module specification from the file location
            spec = importlib.util.spec_from_file_location(module_name, minder_path)
            if spec is None:
                raise ImportError(f"Cannot create module spec for minder at path: {minder_path}")

            # Create a new module based on the specification and load it
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Retrieve the class with the given minder_name from the loaded module
            cls = getattr(module, minder_name, None)
            if cls is None:
                raise ImportError(f"Minder class '{minder_name}' not found in module at {minder_path}")

            return cls

        except Exception as e:
            return None

    def get_minder(self, minder_name: str) -> type | None:
        '''
        Searches for a minder by name and returns its class.

        Steps:
        - Locates the minder directory locally.
        - Reads and parses the minder's TOML configuration file.
        - Extracts required metadata from the config.
        - (Class loading can be implemented here or elsewhere)

        Args:
            minder_name (str): Name of the minder to find.

        Returns:
            type | None: The minder class if found and loaded successfully.

        Raises:
            ValueError: If the minder is not found or if required config parameters are missing.
        '''

        # If the path to a specific minder is not passed, find minders locally
        if not self.minder_path:
            # Get the absolute path to the minder directory
            minder_folder_path = self.search_minder_locally(minder_name)
            if minder_folder_path is None:
                raise ValueError(f"Minder {minder_name} is not installed in {_default_minders_folder}.")
        else:
            # Check minder folder exists
            if not os.path.isfile(os.path.join(self.minder_path, "minder.py")):
                raise FileNotFoundError(f"The minder `{minder_name}` folder was not found on the path `{self.minder_path}`")
            minder_folder_path = self.minder_path
        
        # Load minder class from minder file
        minder_file = f"{minder_folder_path}/minder.py"
        minder_cls = self.load_minder(minder_file, minder_name) # Load minder class from minder file

        if not minder_cls:
            raise ValueError("Minder class not found in minder file")
        
        return minder_cls

class Mind(MinderSearch):
    '''
    The main Mind class of the library.
    Responsible for managing minders and providing dynamic access to them.

    Attributes:
        current_dir (str): Directory of the library file.
        import_dir (str): Directory of the importing script.
        debug_mode (bool): Enables detailed logging if True.
        logger (logging.Logger): Logger instance for debug/info/error messages.
        _dynamic_classes (dict): Cache for dynamically created minder classes.
    '''

    def __init__(
            self,
            path: str | None = None # Accepts the folder path of a specific minders folder
        ):

        self.minder_path = None # Fixed None

        # Dictionary to hold dynamically created minder classes
        self._dynamic_classes = {}

        # Initialize parent class (MinderSearch)
        super().__init__(minders_dir=path)

    def __getattr__(self, name):
        '''
        Override __getattr__ to dynamically create and return minder classes on-demand.

        If a requested attribute (usually a minder class) does not exist, this method:
        - Searches for the minder locally by name.
        - If found, dynamically creates a new class with that name.
        - Caches the class for future access.
        - Returns the new class object.

        Args:
            name (str): Name of the attribute/class requested.

        Returns:
            type: The dynamically created minder class.

        Example:
            mind_instance.SomeMinder  # Automatically creates and returns SomeMinder class if it doesn't exist yet.
        '''
        if name not in self._dynamic_classes:
            minder_cls = self.get_minder(name)
            if minder_cls is None:
                raise AttributeError(f"No minder class found for '{name}'")

            # Кэшировать и вернуть
            self._dynamic_classes[name] = minder_cls

        return self._dynamic_classes[name]

    def load(self, cls: Type[T]) -> T:
        name = cls.__name__
        minder_cls = self.get_minder(name)
        if minder_cls is None:
            raise AttributeError(f"No minder class found for '{name}'")
        return minder_cls()

    def get_version_from_file(self, path):
        """
        Getting the Windows version from __init__.py file without using import
        """

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", content, re.MULTILINE)
        if match:
            return match.group(1)
        raise RuntimeError("Version string not found")