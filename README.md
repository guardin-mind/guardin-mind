![Guardin Mind Framework](docs/assets/mind-logo-without-back.png)

---

**Guardin Mind** is a modern framework for building high-performance **programmatic APIs** using Python.

Unlike REST APIs that operate over HTTP requests, a **programmatic API** uses direct function, method, and class calls, enabling lightning-fast interaction between the client and API as if it were a regular library.

**Key Features:**

* Fast: Extremely high performance — all requests are handled instantly.
* Rapid Development: No need to worry about collisions or type definitions.
* Built-in Package Manager: Install minders directly from GitHub using the built-in package manager.

---

## 🚀 Quick Example Using the HelloWorld Minder

```python
from guardin_mind import Mind
import asyncio

mind = Mind()  # Initialize the framework core
hello_world = mind.HelloWorld()  # Load the HelloWorld minder

# Synchronous request
result = hello_world.ask_sync("Hello via sync")
print(result)

# Asynchronous request
result = asyncio.run(hello_world.ask_async("Hello via async"))
print(result)
```

Before running the code, install the `HelloWorld` minder using the package manager:

```bash
mind install esolment_HelloWorld
```

---

## 📖 Description

The **Guardin Mind** framework enables you to:

* Split your API into independent modules — called **minders**, each acting as a standalone logical API.
* Create flexible, asynchronous, and extensible architectures.
* Build a request queue and handle high-load tasks efficiently.
* Interact with and manage minders via the built-in package manager, allowing easy replacement of API components.
* Use programmatic API instead of traditional REST/HTTP interfaces.

---

## 📚 Documentation

Full documentation is available [here](docs).

---

## ⚙️ System Requirements

* **Minimum Python version**: `3.11.4`
* **Recommended Python version**: `3.13.x`

> Note: Each minder can have its own dependencies, including:
>
> * Specific Python version requirements
> * OS preferences
> * Additional libraries or external tools (e.g., drivers)

The framework is cross-platform, though some minders may have platform-specific requirements.

---

## 📁 Project Structure

```
docs/               # Documentation
guardin_mind/       # Library source code
tests/              # Tests

.gitattributes
.gitignore
LICENSE
pyproject.toml
README.md
requirements-dev.txt
requirements.txt
```

---

## 🛠 Installation

```bash
git clone https://github.com/guardin-mind/guardin-mind
cd guardin-mind
pip install -e .
```

> Installing with the `-e` flag enables editable mode, so any changes to the source code are immediately reflected — perfect for development.

Verify installation:

```bash
mind --version
```

---

## 🧠 Minders

### Importing a Minder

If your minder is located in `~/.guardin-mind/minders` on UNIX or `%USERPROFILE%\.guardin-mind\minders` on Windows, import it as follows:

```python
from guardin_mind import Mind

mind = Mind()
minder = mind.MinderName()  # Replace MinderName with the actual minder name
```

If your minder is installed in a custom directory:

```python
from guardin_mind import Mind

"""
Directory structure:
custom-directory/
    minders/
        MinderName/
            ...minder files...
"""

mind = Mind(path=r"C:\custom-directory")  # Set `path` to the folder that contains the `minders` folder
# Note: Specify the parent directory of `minders`, not `minders` itself.

minder = mind.MinderName()  # Replace MinderName with the actual minder name
```

During development, you can directly import the main minder class in your code and load it:

```python
from .MinderName.minder import MinderName  # Here, MinderName is the name of the main class
from guardin_mind import Mind

mind = Mind()
minder = mind.load(MinderName)  # Pass the main minder class to the `load()` function
```

### Loading a Minder from an External Directory

If the minder is not located inside `guardin_mind/minders`, you can load it manually:

```python
from guardin_mind import Mind

mind = Mind(minder_path="C:/Users/Username/ProjectName/MyMinder")
minder = mind.MyMinder()
```

> Important: In all examples, `MinderName` must **exactly match** the folder name, class name, and minder configuration.

---

## ✨ Creating Your Own Minder

Creating a minder is a simple and fast process:

1. Copy the template folder from `docs/Template`.
2. Rename the `Template` folder to your minder’s name, e.g., `MyMinder`.
3. Open `minder_config.toml` and configure your minder. The `name` parameter **must match** the folder and class name.
4. In `minder.py`, create the main class using the same name as the minder.

> **⚠️ IMPORTANT:**
> The following names must **match exactly**:
>
> * The minder folder name
> * The `name` value in `minder_config.toml`
> * The name of the main class in `minder.py`

### Basic Minder Structure:

```
MyMinder/
│
├── minder_config.toml     # Minder configuration
├── minder.py              # Minder logic (contains the main class)
└── README.md              # Minder description (optional)
```

---

## ✅ Recommended Reading

Explore the [official documentation](docs) for a complete understanding of Guardin Mind’s architecture and capabilities.