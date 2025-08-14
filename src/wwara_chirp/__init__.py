# src/wwara_chirp/__init__.py

from .wwara_chirp import main

# Optional REST API imports - only available if Flask is installed
try:
    from .rest_api import create_app, run_server
    __all__ = ['main', 'create_app', 'run_server']
except ImportError:
    # Flask not available, REST API functionality disabled
    __all__ = ['main']