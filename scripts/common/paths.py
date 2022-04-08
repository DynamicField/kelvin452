from pathlib import Path

scripts_folder = Path(__file__).resolve().parents[1]
project_folder = scripts_folder.parent
venv_folder = project_folder / "venv" / "sus"
venv_scripts_folder = venv_folder / "scripts"
venv_activate_script = scripts_folder / "common" / "activate_this.py"
requirements = project_folder / "requirements.txt"
