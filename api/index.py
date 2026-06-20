"""
Vercel serverless entry point.
Routes all requests to the Flask app defined in app.py.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app  # noqa: F401  — Vercel picks up the `app` WSGI variable
