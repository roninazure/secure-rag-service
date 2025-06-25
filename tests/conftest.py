# tests/conftest.py
import os, sys

# Prepend the project root (one level up) to sys.path so `src` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
