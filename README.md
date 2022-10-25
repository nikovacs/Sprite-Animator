# Sprite Animator:
### v1.0.1-alpha

## About
This program animates sprite sheets!

Supports Windows (>Windows 7) and MacOS.

Supports the following files: ```.gani```

## Installation Instructions:
[Download here](https://github.com/nikovacs/sprite-animator/releases/latest)

If you are using windows, install and run the `SpriteAnimatorSetup64_1.0.1-Alpha.exe`.

If you are using MacOS, download the `SpriteAnimatorSetup64_1.0.1-Alpha.dmg`, open it, then drag the application into the `Applications` folder.
Afterwards, that window can be closed and the `dmg` can be deleted. The Sprite Animator can then be found in the Launchpad or Spotlight search.

On your first time installing v1.0.0 or higher, it will prompt you to navigate to your game folder.

For MacOS users, compatiblity may be an issue if your OS version is prior to `11.5.1 Big Sur`.
If your Mac does not have an Intel CPU, you may need to install `Rosetta` in order for this program to work.
It may prompt you to install Rosetta when you attempt to run the program, or you may have to install it yourself.
To install it yourself, open terminal by pressing `CMD`+`Spacebar` and typing `Terminal` and pressing Return.
Next, type this line: `softwareupdate -install-rosetta -agree-to-license`

#### If there are any issues:
- Please contact me or post an issue [here](https://github.com/nikovacs/sprite-animator/issues)

### NOTE:
This version is still in Alpha and may be unstable. Save often!

## Build from source
Python3 is a pre-requisite for this to work.

To build from source, follow these steps in a command prompt:

`git clone https://github.com/nikovacs/sprite-animator.git`

`cd sprite-animator`

`python3 -m venv .venv`

Windows: `.\.venv\Scripts\Activate`, Mac: `source .venv/bin/activate`

`pip install -r requirements.txt`

(--onedir/one directory mode is preferred as this app relies on external files)
`PyInstaller --onedir --icon=pk_clapper.ico sprite_animator.py -w`

The built program is in the `.\dist` directory

