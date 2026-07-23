"""Skip tests when optional dependencies or services are unavailable."""
import os

try:
    import crawl4ai  # noqa: F401
    _HAS_CRAWL4AI = True
except ImportError:
    _HAS_CRAWL4AI = False

_here = os.path.dirname(os.path.abspath(__file__))
_skip = []
_SERVICE_DIRS = {"docker", "proxy", "mcp", "memory"}
_SERVER_TESTS = {"test_docker.py", "test_main.py"}

# Safe tests: only these exact files can run without crawl4ai
_SAFE_PATHS = {
    os.path.join(_here, "test_cli.py"),
}

for _root, _dirs, _files in os.walk(_here):
    for _f in _files:
        if not (_f.startswith("test_") and _f.endswith(".py")):
            continue
        _path = os.path.join(_root, _f)
        _rel = os.path.relpath(_path, _here)
        _top = _rel.split(os.sep)[0]

        if _top in _SERVICE_DIRS:
            _skip.append(_path)
            continue
        if _f in _SERVER_TESTS:
            _skip.append(_path)
            continue
        if not _HAS_CRAWL4AI and _path not in _SAFE_PATHS:
            _skip.append(_path)

collect_ignore = _skip
