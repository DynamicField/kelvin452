import subprocess
import sys
from common import paths

print("Making sure pyinstaller is installed...")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

print("Creating a package...")
subprocess.check_call(["pyinstaller", paths.project_folder / "game_packaging.spec",
                       "--distpath", paths.project_folder / "packages" / "dist",
                       "--workpath", paths.project_folder / "packages" / "build",
                       "-y"])

print("Package created!")