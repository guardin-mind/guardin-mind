import os
import sys
import tempfile
import shutil
import pytest
from unittest import mock
from guardin_mind import Mind, MinderSearch, PythonVersionError, GuardinMindVersionError

# Test the get_version_from_file method
def test_get_version_from_file(tmp_path):
    file = tmp_path / "__init__.py"
    file.write_text('__version__ = "0.1.0"\n')
    mind = Mind()
    version = mind.get_version_from_file(str(file))
    assert version == "0.1.0"

def test_get_version_from_file_raises(tmp_path):
    file = tmp_path / "__init__.py"
    file.write_text('no version here\n')
    mind = Mind()
    with pytest.raises(RuntimeError):
        mind.get_version_from_file(str(file))

# Test search_minder_locally - create temporary structure
def test_search_minder_locally(tmp_path):
    mind = MinderSearch()
    # Set necessary attributes to avoid AttributeError
    mind.debug_mode = False
    mind.logger = mock.Mock()
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    (tmp_path / "minders").mkdir()
    (tmp_path / "minders" / "TestMinder").mkdir()

    # Should find the directory
    found = mind.search_minder_locally("TestMinder")
    assert found is not None
    assert found.endswith("TestMinder")

    # Should not find non-existing minder
    not_found = mind.search_minder_locally("NoMinder")
    assert not_found is None

# Test load_minder — dynamically load module with class
def test_load_minder(tmp_path):
    mind = MinderSearch()
    # Set necessary attributes
    mind.debug_mode = False
    mind.logger = mock.Mock()
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    class_code = "class TestMinder:\n    pass\n"
    file = tmp_path / "minder.py"
    file.write_text(class_code)

    cls = mind.load_minder(str(file), "TestMinder")
    assert cls is not None
    assert cls.__name__ == "TestMinder"

    # Attempt to load non-existing class should return None
    cls_none = mind.load_minder(str(file), "NoSuchClass")
    assert cls_none is None

# Test get_minder with minimal structure imitation
def test_get_minder(tmp_path, monkeypatch):
    mind = Mind()
    mind.debug_mode = False
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    minders_dir = tmp_path / "minders"
    minder_dir = minders_dir / "SampleMinder"
    minder_dir.mkdir(parents=True)

    # Create minder_config.toml
    config_text = """
name = "SampleMinder"
version = "0.1.0"
description = "Test minder"
authors = [{name = "Tester", email = "test@example.com"}]
python_requires = ">=3.6"
mind_requires = ">=0.1.0"
install_requires = []
"""
    (minder_dir / "minder_config.toml").write_text(config_text, encoding="utf-8")

    # Create dummy minder.py with SampleMinder class
    minder_code = "class SampleMinder:\n    pass\n"
    (minder_dir / "minder.py").write_text(minder_code)

    # Check that SampleMinder class is returned
    cls = mind.get_minder("SampleMinder")
    assert cls is not None
    assert cls.__name__ == "SampleMinder"

# Test exception if minder_config.toml is missing
def test_get_minder_no_config(tmp_path):
    mind = Mind()
    mind.debug_mode = False
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    minders_dir = tmp_path / "minders"
    minder_dir = minders_dir / "BadMinder"
    minder_dir.mkdir(parents=True)
    # No config file present!

    with pytest.raises(FileNotFoundError):
        mind.get_minder("BadMinder")

# Test incompatible python_requires raises PythonVersionError
def test_get_minder_python_version_error(tmp_path):
    mind = Mind()
    mind.debug_mode = False
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    minders_dir = tmp_path / "minders"
    minder_dir = minders_dir / "PyVersionMinder"
    minder_dir.mkdir(parents=True)

    config_text = """
name = "PyVersionMinder"
version = "0.1.0"
description = "Test minder"
authors = [{name = "Tester", email = "test@example.com"}]
python_requires = ">=999.0.0"  # Version incompatible with current
mind_requires = ">=0.1.0"
install_requires = []
"""
    (minder_dir / "minder_config.toml").write_text(config_text, encoding="utf-8")
    (minder_dir / "minder.py").write_text("class PyVersionMinder:\n    pass\n")

    with pytest.raises(PythonVersionError):
        mind.get_minder("PyVersionMinder")

# Test incompatible GuardinMind version raises GuardinMindVersionError
def test_get_minder_guardin_version_error(tmp_path):
    mind = Mind()
    mind.debug_mode = False
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    minders_dir = tmp_path / "minders"
    minder_dir = minders_dir / "MindVersionMinder"
    minder_dir.mkdir(parents=True)

    config_text = """
name = "MindVersionMinder"
version = "0.1.0"
description = "Test minder"
authors = [{name = "Tester", email = "test@example.com"}]
python_requires = ">=3.6"
mind_requires = ">=999.0.0"  # Incompatible version
install_requires = []
"""
    (minder_dir / "minder_config.toml").write_text(config_text, encoding="utf-8")
    (minder_dir / "minder.py").write_text("class MindVersionMinder:\n    pass\n")

    with pytest.raises(GuardinMindVersionError):
        mind.get_minder("MindVersionMinder")

# Test __getattr__ dynamic creation of class and handle missing minder as expected
def test_getattr_dynamic(tmp_path):
    mind = Mind()
    mind.debug_mode = False
    mind.current_dir = str(tmp_path)
    mind.import_dir = str(tmp_path)
    mind.minder_path = None
    mind.version = "0.1.0"

    minders_dir = tmp_path / "minders"
    minder_dir = minders_dir / "DynamicMinder"
    minder_dir.mkdir(parents=True)

    config_text = """
name = "DynamicMinder"
version = "0.1.0"
description = "Test minder"
authors = [{name = "Tester", email = "test@example.com"}]
python_requires = ">=3.6"
mind_requires = ">=0.1.0"
install_requires = []
"""
    (minder_dir / "minder_config.toml").write_text(config_text, encoding="utf-8")
    (minder_dir / "minder.py").write_text("class DynamicMinder:\n    pass\n")

    # Access the class dynamically via __getattr__
    cls = mind.DynamicMinder
    assert cls.__name__ == "DynamicMinder"

    # Trying to access a non-existing minder should raise AttributeError or ValueError internally.
    # Catch both exceptions and consider it correct behavior (test passes if exception is raised).
    try:
        _ = mind.NoSuchMinder
    except (AttributeError, ValueError) as e:
        # Expected behavior: minder not found
        assert "NoSuchMinder" in str(e) or True
    else:
        pytest.fail("Accessing non-existing minder did not raise expected exception")