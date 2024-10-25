from pathlib import Path

serve_path = str(Path(__file__).with_name("serve").resolve())
serve = {"__trame_annotations": serve_path}
scripts = ["__trame_annotations/trame_annotations.umd.cjs"]
vue_use = ["trame_annotations"]
