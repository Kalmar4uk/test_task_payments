import subprocess
import os


def run():
    os.chdir("project")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    subprocess.run(["uvicorn", "settings:app", "--reload"])


if __name__ == "__main__":
    run()
