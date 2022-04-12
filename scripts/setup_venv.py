import subprocess
import venv
import sys
from common.paths import *


def setup_venv(force=False):
    if not venv_folder.exists() or force:
        print("Creating a virtual environment... This may take a while.")
        venv_folder.mkdir()
        venv.create(venv_folder, with_pip=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

    print("Installing pip dependencies...")

    subprocess.run([str(venv_scripts_folder / "pip"), "install", "-r", str(requirements)])


if __name__ == '__main__':
    setup_venv("-f" in sys.argv or "--force" in sys.argv)
