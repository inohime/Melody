<p align="center">
	<img width="150" src="./assets/melody_logo.svg" alt="Melody Banner" />
	<h1 align="center">Melody</h1>
</p>

<div align="center">
	<img src="https://img.shields.io/github/license/inohime/Melody" alt="License" />
	<img src="https://img.shields.io/badge/python-v3.10+-blue?style=flat" alt="Python Badge" />
	<a href="https://github.com/qwertyquerty/pypresence">
		<img 
			src="https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat&logo=discord&logoWidth=20" 
			alt="PyPresence Badge"
		 />
	</a>
	<img 
		src="https://github.com/inohime/Melody/actions/workflows/mel_build.yml/badge.svg?branch=master" 
		alt="CI Status Workflow Badge" 
	/>
</div>

</br>

## Description

A YouTube Music Discord Rich-Presence App utilizing
[PyPresence](https://github.com/qwertyquerty/pypresence) and
[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## Examples

<img width="341" height="233" src="./examples/app_front.png" alt="Melody App Example" />
<img width="341" height="100" src="./examples/(example) song-platonique.png" />
<img width="341" height="155" src="./examples/(example) profile-view-rich-presence.png" />

## Prerequisites

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Get your Application ID
4. Create a new environment variable named `"MELODY_RPC_APP_ID"` and
   add the Application ID as the value.
5. Python version `3.10 or higher` is required. For `Linux (aarch64)`,
   skip to [this](#linux-aarch64) section
6. Install the dependencies:
   
   ```shell
   # Append `pyobjc` for MacOS
   pip install pyinstaller requests-html lxml numpy dearpygui beautifulsoup4 pypresence Pillow
   ```

Continue onto [Building](#building)

## Building

### Windows/MacOS

Build & Install the application:

```shell
# Use in root directory
pyinstaller -n melody --windowed --icon=assets/dmi.ico -F src/mel.py
```

If the build fails, it may be due to the packages not being located.
To resolve this, supply the directory of your python site-packages to the paths flag:

```shell
# Ex.) --paths=C:/Python311/Lib/site-packages
--paths={PATH_TO_YOUR_PYTHON_LIB_SITE-PACKAGES}
```

Continue to [Setup](#setup-melody)

### Linux (aarch64)

Both Discord & Google Chrome do not support `Linux (aarch64)`, opt for their alternatives:
   - ArmCord
   - Chromium

Some of the dependencies are not supported in `python 3.11` for this platform,
use `pyenv` to get a python version between `3.10` & `3.10.11` to install these packages.

Create a new python virtual environment:

```python
python3.10 -m venv ~/{DIRECTORY_NAME}/
```

Build `dearpygui` wheel from source as it lacks a package for this platform:

1. Install the wheel package:

   ```shell
   pip3.10 install wheel
   ```

2. Build `dearpygui` from source:
   1. Get the repository:

      ```shell
      git clone --recursive https://github.com/hoffstadt/DearPyGui && cd DearPyGui
      ```

   2. Install the necessary libs:

      ```shell
      sudo apt install -y cmake libglu1-mesa-dev libgl1-mesa-dev \
      libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev
      ```

   3. Build the wheel:

      ```shell
      python3.10 -m setup bdist_wheel --dist-dir {OUTPUT_DIST_DIRECTORY}
      ```

   4. Install the package:

      ```shell
      pip3.10 install {OUTPUT_DIST_DIRECTORY}/dearpygui-1.9.2-cp310-cp310-linux_aarch64.whl
      ```


> [!IMPORTANT]\
> The application requires `requests-html` to work.\
> The chromium that comes with the package doesn't support aarch64.

To fix this, `requests_html.py` will need to be modified:
   -  Add `"executablePath="/snap/bin/chromium"`
      or the directory of your chromium executable
      as the first argument to `pyppteer.launch()` in the `browser` property in `BaseSession`

Setup Discord IPC:

```shell
mkdir -p ~/.config/user-tmpfiles.d
echo 'L %t/discord-ipc-0 - - - - .flatpak/xyz.armcord.ArmCord/xdg-run/discord-ipc-0' > \
~/.config/user-tmpfiles.d/discord-rpc.conf
systemctl --user enable --now systemd-tmpfiles-setup.service
```

Build & Install the application:

```shell
# Using pyinstaller package from python virtual environment bin
./pyinstaller -n melody --windowed -F ~/Melody/src/mel.py \
--distpath=~/Melody/dist/ --specpath=~/Melody/ --workpath=~/Melody/build/
```

Continue to [Setup](#setup-melody)

## Setup Melody

1. Unzip the `assets` directory into the `dist` output directory
2. Open YouTube Music and Rich Presence will showcase what you're listening to!

## Important Additional Info

- Firefox & LibreWolf in MacOS/Linux update the history database infrequently,
  the current song shown will be inaccurate
  - Test cases that make browser update the history database:
    - Search then close tab
    - Close browser

- Rich Presence only updates once every 15 seconds (per Discord API limit)

- Prefer to close the application normally instead of using the quit button
  (both do the same thing, dearpygui framework limitation)
  - If you decide to use the quit button, wait 5 seconds before closing the application

- If there is no album title found, the song's title will be used as the album title

- If 11 URLs are visited, the application will assume you have paused the media session,
  you will need to reload the tab or select another song

- Currently, the application does not check if discord is closed (should this happen,
  you will need to close the chromium instances created by the application)

## Acknowledgements

Background photo by
<a href="https://unsplash.com/@hisevil">Agata Ciosek</a> on
<a href="https://unsplash.com">Unsplash</a>

Icons by:

- <a href="https://twitter.com/codecalm">Paweł Kuna</a> on
  <a href="https://tablericons.com">Tabler Icons</a>
- <a href="https://preciousm.co/">Precious & Solomon</a> on
  <a href="https://basicons.xyz">Basicons</a>
