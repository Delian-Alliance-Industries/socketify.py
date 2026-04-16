## 📦 Installation
For macOS x64 & Silicon, Linux x64, Windows

```bash
pip install delian-socketify
#or specify PyPy3
pypy3 -m pip install delian-socketify
#or in editable mode
pypy3 -m pip install -e .
```

Using install via requirements.txt
```text
delian-socketify
```
```bash
pip install -r ./requirements.txt
#or specify PyPy3
pypy3 -m pip install -r ./requirements.txt
```

The Python import name remains `socketify`:

```python
from socketify import App
```

If you are using linux or macOS, you may need to install libuv and zlib in your system

macOS
```bash
brew install libuv
brew install zlib
```

Linux
```bash
apt install libuv1 zlib1g
```


### Next [Getting Started](getting-started.md)
