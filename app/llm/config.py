"""
Configuration loader for LLM clients.
Loads environment variables from .env file.
"""

from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_env_file(env_path: Optional[str | Path] = None) -> None:
    """
    Load environment variables from .env file.
    
    Args:
        env_path: Path to .env file. If None, looks for .env in project root.
    """
    if load_dotenv is None:
        # python-dotenv not installed, skip loading
        return
    
    if env_path is None:
        # Find project root (look for .env file)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent  # app/llm -> app -> project_root
        env_path = project_root / ".env"
    else:
        env_path = Path(env_path)
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)


# Load .env file when module is imported
load_env_file()

