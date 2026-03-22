from pathlib import Path
from .inkind_knowledge_repo import *

THIS_PATH = Path(__file__).parent

SCHEMA_DIRECTORY = THIS_PATH.parent / "schema"
MAIN_SCHEMA_PATH = SCHEMA_DIRECTORY / "inkind_knowledge_repo.yaml"
