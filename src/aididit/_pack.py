"""Where the bundled Spec Kit extension lives and what it is called once installed."""

from pathlib import Path

PACK_DIR = Path(__file__).resolve().parent / "pack"
EXTENSION_ID = "aididit"
LANE_WORKFLOW_ID = "aididit-lane"
LANE_WORKFLOW_FILE = Path("workflows") / f"{LANE_WORKFLOW_ID}.yml"
BOARD_TEMPLATE = Path("templates") / "board.md"
PROJECT_STATE_DIR = Path(".specify") / "aididit"
SPECKIT_DIR = ".specify"
CONSTITUTION = Path(SPECKIT_DIR) / "memory" / "constitution.md"
CONSTITUTION_TEMPLATE_MARK = "[PROJECT_NAME]"  # the first line of Spec Kit's unfilled template
SPECKIT_INSTALL_HINT = "uv tool install specify-cli  (or reinstall: uv tool install --force ai-did-it)"
