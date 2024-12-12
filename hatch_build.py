from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import subprocess


class BuildFrontend(BuildHookInterface):
    PLUGIN_NAME = "build_frontend"
    FRONTEND_DIR_PATH = "vue-components"

    def initialize(self, version, build_data):
        subprocess.run(
            args=["npm", "install"],
            cwd=str(Path(__file__).with_name(self.FRONTEND_DIR_PATH).resolve()),
            check=True,
        )
        subprocess.run(
            args=["npm", "run", "build"],
            cwd=str(Path(__file__).with_name(self.FRONTEND_DIR_PATH).resolve()),
            check=True,
        )

        return super().initialize(version, build_data)
