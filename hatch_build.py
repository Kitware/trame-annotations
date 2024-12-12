import sys
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess


class BuildFrontend(BuildHookInterface):
    PLUGIN_NAME = "build_frontend"
    FRONTEND_DIR_PATH = "vue-components"

    def initialize(self, version, build_data):
        npm_cmd = "npm.cmd" if sys.platform.startswith("win") else "npm"
        work_dir = str((Path(self.root) / self.FRONTEND_DIR_PATH).resolve())
        print(f"Run build commands in {work_dir}")
        subprocess.run(
            args=[npm_cmd, "install"],
            cwd=work_dir,
            check=True,
        )
        subprocess.run(
            args=[npm_cmd, "run", "build"],
            cwd=work_dir,
            check=True,
        )

        return super().initialize(version, build_data)
