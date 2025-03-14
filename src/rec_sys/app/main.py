"""Module to make calls to the interface."""

import os
from pathlib import Path


def run_app():
    """A launcher function that calls 'streamlit run' on the app.py file.

    This is what we'll expose in pyproject.toml.
    """
    script_path = Path(__file__).parent.absolute() / "app.py"
    # Use os.system or subprocess to invoke the Streamlit CLI
    os.system(f'streamlit run "{script_path}"')
