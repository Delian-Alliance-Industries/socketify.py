# socketify.py (delian-socketify)

<p align="center">
  <a href="https://github.com/Delian-Alliance-Industries/socketify.py"><img src="https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/logo.png" alt="Logo" height=170></a>
  <br />
  <br />
<a href='https://pypi.org/project/delian-socketify/' target="_blank"><img alt='PyPI' src='https://img.shields.io/pypi/v/delian-socketify.svg'></a>
</p>

<div align="center">
  <a href="https://github.com/Delian-Alliance-Industries/socketify.py">Github</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://github.com/Delian-Alliance-Industries/socketify.py/issues">Issues</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://github.com/Delian-Alliance-Industries/socketify.py/tree/main/examples">Examples</a>
  <br />
</div>

> This is a maintained fork of [`cirospaciari/socketify.py`](https://github.com/cirospaciari/socketify.py) published to PyPI as [`delian-socketify`](https://pypi.org/project/delian-socketify/). The Python import name remains `socketify`, so existing code keeps working unchanged. All credit for the original work goes to Ciro Spaciari and contributors; this fork only packages and maintains it under a new distribution name.

## 💡 Features

- WebSocket with pub/sub support
- Fast and reliable Http/Https
- Support for Windows, Linux and macOS Silicon & x64
- Support for [`PyPy3`](https://www.pypy.org/) and [`CPython`](https://github.com/python/cpython)
- Dynamic URL Routing with Wildcard & Parameter support
- Sync and Async Function Support
- Really Simple API
- Fast and Encrypted TLS 1.3 quicker than most alternative servers can do even unencrypted, cleartext messaging
- Per-SNI HttpRouter Support
- Proxy Protocol v2
- Shared or Dedicated Compression Support
- Max Backpressure, Max Timeout, Max Payload and Idle Timeout Support
- Automatic Ping / Pong Support
- Per Socket Data
- [`Middlewares`](https://docs.socketify.dev/middlewares.html)
- [`Templates`](https://docs.socketify.dev/templates.html) Support (examples with [`Mako`](https://github.com/Delian-Alliance-Industries/socketify.py/tree/main/examples/template_mako.py) and [`Jinja2`](https://github.com/Delian-Alliance-Industries/socketify.py/tree/main/examples/template_jinja2.py))
- [`ASGI Server`](https://docs.socketify.dev/cli.html)
- [`WSGI Server`](https://docs.socketify.dev/cli.html)
- [`Plugins/Extensions`](https://docs.socketify.dev/extensions.html)

## :mag_right: Upcoming Features

- In-Memory Cache Tools
- Fetch like API powered by libuv
- Async file IO powered by libuv
- Full asyncio integration with libuv
- SSGI Server spec and support
- RSGI Server support
- Full Http3 support
- [`HPy`](https://hpyproject.org/) integration to better support [`CPython`](https://github.com/python/cpython), [`PyPy`](https://www.pypy.org/) and [`GraalPython`](https://github.com/oracle/graalpython)
- Hot Reloading

We created and adapted the full C API from [uNetworking/uWebSockets](https://github.com/uNetworking/uWebSockets) and will integrate libuv powered fetch and file IO, this same C API is used by [Bun](https://bun.sh/)

## :zap: Benchmarks

Socketify WebFramework HTTP requests per second (Linux x64)

![image](https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/bench-bar-graph-general.png)

WSGI Server requests per second (Linux x64)

![image](https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/bench-bar-graph-wsgi.png)

ASGI Server requests per second (Linux x64)

![image](https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/bench-bar-graph-asgi.png)

WebSocket messages per second (Linux x64)

![image](https://raw.githubusercontent.com/cirospaciari/socketify.py/main/misc/bench-bar-graph-websockets.png)

Http tested with TFB tool plaintext benchmark<br/>
WebSocket tested with [Bun.sh](https://bun.sh) bench chat-client <br/>
Source code in [TechEmPower](https://github.com/TechEmpower/FrameworkBenchmarks) and for websockets in [bench](https://github.com/Delian-Alliance-Industries/socketify.py/tree/main/bench)<br/>

Machine OS: Debian GNU/Linux bookworm/sid x86_64 Kernel: 6.0.0-2-amd64 CPU: Intel i7-7700HQ (8) @ 3.800GHz Memory: 32066MiB

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

If you are using linux or macOS, you may need to install libuv and zlib in your system

macOS

```bash
brew install libuv
brew install zlib
```

Linux (Ubuntu/Debian)

```bash
apt install libuv1 zlib1g
```

Linux (RHEL/OEL)

```bash
yum install cmake zlib-devel libuv-devel
```

## 🤔 Usage

Hello world app

```python
from socketify import App

app = App()
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % config.port))
app.run()
```

SSL version sample

``` python
from socketify import App, AppOptions

app = App(AppOptions(key_file_name="./misc/key.pem", cert_file_name="./misc/cert.pem", passphrase="1234"))
app.get("/", lambda res, req: res.end("Hello World socketify from Python!"))
app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % config.port))
app.run()
```

WebSockets

```python
from socketify import App, OpCode, CompressOptions

def ws_open(ws):
    print('A WebSocket got connected!')
    ws.send("Hello World!", OpCode.TEXT)

def ws_message(ws, message, opcode):
    #Ok is false if backpressure was built up, wait for drain
    ok = ws.send(message, opcode)

app = App()
app.ws("/*", {
    'compression': CompressOptions.SHARED_COMPRESSOR,
    'max_payload_length': 16 * 1024 * 1024,
    'idle_timeout': 12,
    'open': ws_open,
    'message': ws_message,
    'drain': lambda ws: print(f'WebSocket backpressure: {ws.get_buffered_amount()}'),
    'close': lambda ws, code, message: print('WebSocket closed'),
    'subscription': lambda ws, topic, subscriptions, subscriptions_before: print(f'subscribe/unsubscribe on topic {topic} {subscriptions} {subscriptions_before}'),
})
app.any("/", lambda res,req: res.end("Nothing to see here!'"))
app.listen(3000, lambda config: print("Listening on port http://localhost:%d now\n" % (config.port)))
app.run()
```

We have more than 20 examples [click here](https://github.com/Delian-Alliance-Industries/socketify.py/tree/main/examples) for more

## :hammer: Building from source

```bash
#clone and update submodules
git clone https://github.com/Delian-Alliance-Industries/socketify.py.git
cd ./socketify.py
git submodule update --init --recursive --remote
#you can use make linux, make macos or call Make.bat from Visual Studio Development Prompt to build
cd ./src/socketify/native/ && make linux && cd ../../../
#install local pip
pypy3 -m pip install .
#install in editable mode
pypy3 -m pip install -e .
#if you want to remove
pypy3 -m pip uninstall delian-socketify
```

## :page_facing_up: Attribution

Original project: [cirospaciari/socketify.py](https://github.com/cirospaciari/socketify.py) by Ciro Spaciari. Licensed under the MIT License (see [LICENSE](./LICENSE)).

Special thanks to [uNetworking AB](https://github.com/uNetworking) for [uWebSockets](https://github.com/uNetworking/uWebSockets) and [uSockets](https://github.com/uNetworking/uSockets), which power this library.

## :grey_question: uvloop

We don't use uvloop, because uvloop doesn't support Windows and PyPy3 at this moment; this may change in the future, but right now we want to implement our own libuv + asyncio solution, and a lot more.

## :dizzy: CFFI vs Cython vs HPy

Cython performs really well on Python3 but really bad on PyPy3. CFFI was chosen for better PyPy3 support until we get our hands on a stable [`HPy`](https://hpyproject.org/) integration.
