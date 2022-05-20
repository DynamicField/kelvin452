from common.paths import *
import subprocess
import os
from setup_venv import setup_venv

if not venv_folder.exists():
    print("The virtual environment doesn't exist! We'll set it up.")
    setup_venv()

python_file_name = "python.exe" if os.name == "nt" else "python"
new_env = dict(os.environ)
new_env["PYTHONPATH"] = new_env.get("PYTHONPATH", "") + os.pathsep + str(project_folder / "src")

subprocess.run([venv_scripts_folder / python_file_name, "-m", "kelvin452.game"],
               env=new_env)
