import os
import platform
from mel_browser import mbp


DEVELOPER_APP_ID = os.getenv("MELODY_RPC_APP_ID")

APP_PATH = os.path.join(os.getcwd())
APP_NAME = "Melody"
APP_ICON = APP_PATH + "/assets/" + "dmi.ico"

ASSET_PATH = APP_PATH + "/assets/"

HCOPY_FILENAME = "melody_history_copy"

# --> Arc
USER_ARC_DIR = mbp.arc_dir
ARC_HISTORY_PATH = USER_ARC_DIR + "History"
ARC_HISTORY_COPY_PATH = USER_ARC_DIR + HCOPY_FILENAME

# --> Chrome
USER_CHROME_DIR = mbp.chrome_dir
CHROME_HISTORY_PATH = USER_CHROME_DIR + "History"
CHROME_HISTORY_COPY_PATH = USER_CHROME_DIR + HCOPY_FILENAME

# --> Chromium
USER_CHROMIUM_DIR = mbp.chromium_dir
CHROMIUM_HISTORY_PATH = USER_CHROMIUM_DIR + "History"
CHROMIUM_HISTORY_COPY_PATH = USER_CHROMIUM_DIR + HCOPY_FILENAME


# --> MSEdge
USER_EDGE_DIR = mbp.edge_dir
EDGE_HISTORY_PATH = USER_EDGE_DIR + "History"
EDGE_HISTORY_COPY_PATH = USER_EDGE_DIR + HCOPY_FILENAME


# --> Firefox
USER_FIREFOX_DIR = mbp.firefox_dir
FIREFOX_HISTORY_PATH = USER_FIREFOX_DIR + "places.sqlite"
FIREFOX_HISTORY_COPY_PATH = f"{USER_FIREFOX_DIR}{HCOPY_FILENAME}.sqlite"


# --> LibreWolf
USER_LIBREWOLF_DIR = mbp.librewolf_dir
LIBREWOLF_HISTORY_PATH = USER_LIBREWOLF_DIR + "places.sqlite"
LIBREWOLF_HISTORY_COPY_PATH = f"{USER_LIBREWOLF_DIR}{HCOPY_FILENAME}.sqlite"


if platform.system() == "Darwin":
    # --> Safari
    USER_SAFARI_DIR = mbp.safari_dir
    SAFARI_HISTORY_PATH = USER_SAFARI_DIR + "History.db"


WIDTH = 450
HEIGHT = 280