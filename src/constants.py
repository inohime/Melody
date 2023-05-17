import os

DEVELOPER_APP_ID = os.getenv("MELODY_RPC_APP_ID")

APP_PATH = os.path.join(os.getcwd())
APP_NAME = "Melody"
APP_ICON = APP_PATH + "/assets/" + "dmi.ico"

ASSET_PATH = APP_PATH + "/assets/"

# NOTE: get the vars for macOS and Ubuntu to make this cross platform

HCOPY_FILENAME = "melody_history_copy"

# windows specific
WIN_USER_PATH = os.getenv("USERPROFILE")


# --> Chrome
WIN_USER_CHROME_DIR = WIN_USER_PATH + \
    "/AppData/Local/Google/Chrome/User Data/Default/"

WIN_CHROME_HISTORY_PATH = WIN_USER_CHROME_DIR + "History"
WIN_CHROME_HISTORY_COPY_PATH = WIN_USER_CHROME_DIR + HCOPY_FILENAME


# --> MSEdge
WIN_USER_EDGE_DIR = WIN_USER_PATH + \
    "/AppData/Local/Microsoft/Edge/User Data/Default/"

WIN_EDGE_HISTORY_PATH = WIN_USER_EDGE_DIR + "History"
WIN_EDGE_HISTORY_COPY_PATH = WIN_USER_EDGE_DIR + HCOPY_FILENAME


# --> Firefox
WIN_USER_FIREFOX_PARTIAL_DIR = WIN_USER_PATH + \
    "/AppData/Roaming/Mozilla/Firefox/Profiles"

WIN_USER_FIREFOX_DIR = [
    os.path.join(WIN_USER_FIREFOX_PARTIAL_DIR, dir)
    for dir in os.listdir(WIN_USER_FIREFOX_PARTIAL_DIR)
    if os.path.isdir(os.path.join(WIN_USER_FIREFOX_PARTIAL_DIR, dir))
][0]
WIN_FIREFOX_HISTORY_PATH = WIN_USER_FIREFOX_DIR + "/places.sqlite"


# --> LibreWolf
WIN_USER_LIBREWOLF_PARTIAL_DIR = WIN_USER_PATH + \
    "/AppData/Roaming/librewolf/Profiles"

WIN_USER_LIBREWOLF_DIR = [
    os.path.join(WIN_USER_LIBREWOLF_PARTIAL_DIR, dir)
    for dir in os.listdir(WIN_USER_LIBREWOLF_PARTIAL_DIR)
    if os.path.isdir(os.path.join(WIN_USER_LIBREWOLF_PARTIAL_DIR, dir))
][0]
WIN_LIBREWOLF_HISTORY_PATH = WIN_USER_LIBREWOLF_DIR + "/places.sqlite"


WIDTH = 450
HEIGHT = 280
