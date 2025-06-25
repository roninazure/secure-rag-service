# tests/conftest.py

import os
import sys

# add project root to the import path
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
    )
)
sys.path.insert(0, PROJECT_ROOT)
