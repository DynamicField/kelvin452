from pathlib import Path
import os 

venv_binaries_folder_name = "Scripts" if os.name == "nt" else "bin" 

scripts_folder = Path(__file__).resolve().parents[1]
project_folder = scripts_folder.parent
venv_folder = project_folder / "venv"
venv_scripts_folder = venv_folder / venv_binaries_folder_name
venv_activate_script = scripts_folder / "common" / "activate_this.py"
requirements = project_folder / "requirements.txt"
