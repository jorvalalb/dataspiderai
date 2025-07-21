# tests/test_version.py

import re
import pytest
from dataspiderai.__version__ import __version__

def test_version_is_string():
    """La variable __version__ debe ser una cadena."""
    assert isinstance(__version__, str), "__version__ debe ser un str"

def test_version_semver_format():
    """
    La versión debe seguir al menos un esquema semántico mínimo: X.Y.Z
    Opcionalmente puede llevar más texto (por ejemplo, '1.2.3-dev').
    """
    # Esto acepta '1.2.3' o '1.2.3-alpha.1', etc.
    semver_regex = r"^\d+\.\d+\.\d+([\-\.][0-9A-Za-z]+)*$"
    assert re.match(semver_regex, __version__), f"Versión inválida: {__version__}"
