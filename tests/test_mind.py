import os
import tempfile
import types
import pytest
from guardin_mind import MinderSearch, Mind

# Helper function to create a minder folder structure
def create_minder_dir(base_dir, minder_name, minder_code=None):
    minder_dir = os.path.join(base_dir, "minders", minder_name)
    os.makedirs(minder_dir, exist_ok=True)
    minder_file = os.path.join(minder_dir, "minder.py")
    if minder_code is None:
        # By default, create a simple class with the same name as the minder
        minder_code = f"class {minder_name}:\n    pass\n"
    with open(minder_file, "w", encoding="utf-8") as f:
        f.write(minder_code)
    return minder_dir, minder_file

def test_search_minder_locally():
    with tempfile.TemporaryDirectory() as tmpdir:
        minders_dir = os.path.join(tmpdir, "minders")
        os.makedirs(minders_dir)
        # Create a minder
        minder_name = "TestMinder"
        os.makedirs(os.path.join(minders_dir, minder_name))
        
        ms = MinderSearch(minders_dir=tmpdir)
        found_path = ms.search_minder_locally(minder_name)
        assert found_path is not None
        assert found_path.endswith(f"minders/{minder_name}")

        # Search for a non-existent minder
        assert ms.search_minder_locally("NoSuchMinder") is None

def test_load_minder_success_and_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        minder_name = "TestMinder"
        _, minder_file = create_minder_dir(tmpdir, minder_name, 
            minder_code=f"class {minder_name}:\n    def hello(self): return 'hi'\n")

        ms = MinderSearch(minders_dir=tmpdir)
        cls = ms.load_minder(minder_file, minder_name)
        assert cls is not None
        instance = cls()
        assert instance.hello() == "hi"

        # Try to load a class with the wrong name
        cls_none = ms.load_minder(minder_file, "WrongName")
        assert cls_none is None

def test_get_minder_success_and_fail(tmp_path):
    minder_name = "TestMinder"
    create_minder_dir(tmp_path, minder_name)

    ms = MinderSearch(minders_dir=tmp_path)

    # Set minder_path to None to use local search
    ms.minder_path = None
    cls = ms.get_minder(minder_name)
    assert cls is not None
    assert cls.__name__ == minder_name

    # Check for exception if minder not found
    with pytest.raises(ValueError):
        ms.get_minder("NoSuchMinder")

def test_mind_dynamic_loading(tmp_path):
    minder_name = "DynamicMinder"
    create_minder_dir(tmp_path, minder_name)

    mind = Mind(path=tmp_path)
    # Accessing the attribute dynamically loads the class
    cls = getattr(mind, minder_name)
    assert cls.__name__ == minder_name

    # Check caching — subsequent access returns the same class
    cls2 = getattr(mind, minder_name)
    assert cls is cls2

    # Check for exception when requesting a non-existent minder
    with pytest.raises(ValueError):
        getattr(mind, "NoSuchMinder")

def test_load_method_returns_instance(tmp_path):
    minder_name = "LoadMinder"
    create_minder_dir(tmp_path, minder_name)

    mind = Mind(path=tmp_path)
    cls = getattr(mind, minder_name)
    instance = mind.load(cls)
    assert instance.__class__.__name__ == minder_name

def test_get_version_from_file(tmp_path):
    version_file = tmp_path / "__init__.py"
    version_file.write_text("__version__ = '1.2.3'")

    mind = Mind()
    version = mind.get_version_from_file(str(version_file))
    assert version == "1.2.3"

    # Check for exception if version string is not found
    bad_file = tmp_path / "bad_init.py"
    bad_file.write_text("no version here")
    with pytest.raises(RuntimeError):
        mind.get_version_from_file(str(bad_file))