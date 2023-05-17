import os

# commented out = untested
bind = {
    "FIREFOX": "Gecko",
    "CHROME": "Blink",
    # "SAFARI": "WebKit",
    "LIBREWOLF": "Gecko",
    "MSEDGE": "Blink",
}


def fetch_browser():
    try:
        if os.name == "nt":
            import winreg as win

            with win.OpenKey(
                win.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
            ) as reg_key:
                default = win.QueryValueEx(reg_key, "ProgId")[0]

            with win.OpenKey(
                win.HKEY_CLASSES_ROOT,
                r"{}\shell\open\command".format(default)
            ) as reg_key:
                default_path_vals = win.QueryValueEx(reg_key, None)
                default_path = default_path_vals[0].split('"')[1]

                return detect_browser_renderer(
                    default_path.rsplit("\\", 1)[1].split(".exe")[0]
                )
        else:
            # impl posix
            pass

    except Exception as e:
        print(f"Failed to get default browser: {e}")
        return None


def detect_browser_renderer(browser: str):
    binder = browser.upper()
    return (binder, bind[binder])
