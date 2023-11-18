import os
import platform
from abc import ABC, abstractmethod


bind = {
    # CHROME is Chromium, it 
    # reports differently compared to google chrome
    "CHROME": "Blink",
    "CHROM": "Blink",
    "MSEDGE": "Blink",
    "FIREFOX": "Gecko",
    "LIBREWOLF": "Gecko",
    "SAFARI": "WebKit",
}


class IMelodyBP(ABC):
    def __init__(self) -> None:
        super().__init__()

        self.chromium_path = ""
        self.chrome_path = ""
        self.edge_path = ""
        self.firefox_path = ""
        self.librewolf_path = ""

    @abstractmethod
    def user_path(self) -> str:
        '''
        returns path to the user's home directory
        '''
        pass

    @property
    @abstractmethod
    def chromium_dir(self) -> str:
        '''
        returns path of the user's Chromium directory
        '''
        return self.user_path() + self.chromium_path

    @property
    @abstractmethod
    def chrome_dir(self) -> str:
        '''
        returns path of the user's Chrome directory
        '''
        return self.user_path() + self.chrome_path

    @property
    @abstractmethod
    def edge_dir(self) -> str:
        '''
        returns path of the user's MSEdge directory
        '''
        return self.user_path() + self.edge_path

    @property
    @abstractmethod
    def firefox_dir(self) -> str:
        '''
        returns path of the user's Firefox directory
        '''
        partial_dir = self.user_path() + self.firefox_path

        # used to skip should the directory/app (firefox) not exist
        if not os.path.exists(partial_dir):
            return ""

        # NOTE: default profile is found by profiles.ini -> [Install(...)] Default=...
        #       this just finds the first one with a places.sqlite

        return f'''{[
            os.path.join(partial_dir, dir)
            for dir in os.listdir(partial_dir)
            if os.path.exists(os.path.join(partial_dir, dir + '/places.sqlite'))
        ][0]}/'''

    @property
    @abstractmethod
    def librewolf_dir(self) -> str:
        '''
        returns path of the user's LibreWolf directory
        '''
        partial_dir = self.user_path() + self.librewolf_path

        if not os.path.exists(partial_dir):
            return ""

        return f'''{[
            os.path.join(partial_dir, dir)
            for dir in os.listdir(partial_dir)
            if os.path.exists(os.path.join(partial_dir, dir + '/places.sqlite'))
        ][0]}/'''


class MelodyBPWindows(IMelodyBP):
    def __init__(self) -> None:
        super().__init__()

        # gecko-based browsers don't have a forward-slash appended until
        # after property invoked due to the OS operations in the base class
        self.chromium_path = "/AppData/Local/Chromium/User Data/Default/"
        self.chrome_path = "/AppData/Local/Google/Chrome/User Data/Default/"
        self.edge_path = "/AppData/Local/Microsoft/Edge/User Data/Default/"
        self.firefox_path = "/AppData/Roaming/Mozilla/Firefox/Profiles"
        self.librewolf_path = "/AppData/Roaming/librewolf/Profiles"

    def user_path(self) -> str:
        return os.getenv("USERPROFILE")

    @property
    def chromium_dir(self) -> str:
        return super().chromium_dir

    @property
    def chrome_dir(self) -> str:
        return super().chrome_dir

    @property
    def edge_dir(self) -> str:
        return super().edge_dir

    # non literals should be local static (cached)
    # so we don't have to recompute and make our constants "fake"
    @property
    def firefox_dir(self) -> str:
        return super().firefox_dir

    @property
    def librewolf_dir(self) -> str:
        return super().librewolf_dir


class MelodyBPMacOS(IMelodyBP):
    def __init__(self) -> None:
        super().__init__()

        self.chrome_path = "/Library/Application Support/Google/Chrome/Default/"
        self.edge_path = "/Library/Application Support/Microsoft/Edge/Default/"
        self.firefox_path = "/Library/Application Support/Firefox/Profiles"
        self.librewolf_path = "/Library/Application Support/librewolf/Profiles"
        self.safari_path = "/Library/Safari/"

    def user_path(self) -> str:
        return os.getenv("HOME")
    
    @property
    def chromium_dir(self) -> str:
        # don't feel like dealing with this (platform) rn
        return super().chromium_dir

    @property
    def chrome_dir(self) -> str:
        return super().chrome_dir

    @property
    def edge_dir(self) -> str:
        return super().edge_dir

    @property
    def firefox_dir(self) -> str:
        return super().firefox_dir

    @property
    def librewolf_dir(self) -> str:
        return super().librewolf_dir

    @property
    def safari_dir(self) -> str:
        return self.user_path() + self.safari_path


class MelodyBPLinux(IMelodyBP):
    def __init__(self) -> None:
        super().__init__()

        self.chromium_path = "/snap/chromium/common/chromium/Default/"
        self.chrome_path = self.chromium_path
        self.firefox_path = ""
        self.librewolf_path = ""

    def user_path(self) -> str:
        return os.getenv("HOME")
    
    @property
    def chromium_dir(self) -> str:
        # uses chromium since google chrome isn't supported on aarch64
        return super().chromium_dir

    @property
    def chrome_dir(self) -> str:
        # uses chromium since google chrome isn't supported on aarch64
        return super().chrome_dir

    @property
    def edge_dir(self) -> str:
        raise RuntimeError(
            f'''
            Currently not supported due to
            aarch64 limitation and
            other MSEdge releases limited to amd64 binaries
            '''
        )

    @property
    def firefox_dir(self) -> str:
        snap_firefox_dir = "snap/firefox"
        if os.path.exists(os.path.join(self.user_path(), snap_firefox_dir)):
            self.firefox_path = f"/{snap_firefox_dir}/common/.mozilla/firefox"
        else:
            # for when firefox was installed outside of snap
            self.firefox_path = "/.mozilla/firefox"

        return super().firefox_dir

    @property
    def librewolf_dir(self) -> str:
        flatpak_librewolf_dir = ".var/app/io.gitlab.librewolf-community/.librewolf"
        if os.path.exists(os.path.join(self.user_path(), flatpak_librewolf_dir)):
            self.librewolf_path = f"/{flatpak_librewolf_dir}"
        else:
            raise RuntimeError(
                f'''
                Only Flatpak is supported due to 
                aarch64 limitation and
                other LibreWolf releases limited to amd64 binaries
                '''
            )

        return super().librewolf_dir


def fetch_browser() -> tuple[str, str] | None:
    try:
        match platform.system():
            case "Windows":
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

            case "Darwin":
                from AppKit import NSWorkspace
                from Cocoa import NSURL
                from Foundation import NSBundle

                url = NSWorkspace.sharedWorkspace().URLForApplicationToOpenURL_(
                    NSURL.URLWithString_("http://")
                )
                bundle = NSBundle.bundleWithPath_(url.path())

                return detect_browser_renderer(
                    bundle.bundlePath().split('/')[-1].split('.')[0]
                )

            case "Linux":
                import subprocess

                output = subprocess.check_output(
                    ["xdg-settings", "get", "default-web-browser"]
                )
                app_name = output.decode().strip()

                for x in bind:
                    if x.lower() in app_name.lower():
                        return detect_browser_renderer(x)

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def detect_browser_renderer(browser: str) -> tuple[str, str]:
    binder = browser.upper()
    if binder.find(' ') != -1:
        # for when browser name has a space in it, like "GOOGLE CHROME"
        # then take the right str as it typically has the name we want
        # (edge in microsoft edge, chrome)
        binder = binder.split(' ')[1]

    return (binder, bind[binder])


def acquire_platform_type() -> IMelodyBP | NotImplementedError:
    match platform.system():
        case "Windows":
            return MelodyBPWindows()

        case "Darwin":
            return MelodyBPMacOS()

        case "Linux":
            return MelodyBPLinux()

        case _:
            return NotImplementedError("This platform is not supported!")


mbp = acquire_platform_type()
'''
#### Melody Browser Platform variable 
returns the appropriate browser platform (Windows, MacOS, Linux)
'''
