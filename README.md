# Lurlene
Python-based live-coding language optimised for a small number of channels.

## Install
These are generic installation instructions.

### To use, disposably
Install the current release from PyPI to a virtual environment:
```
python3 -m venv venvname
venvname/bin/pip install -U pip
venvname/bin/pip install Lurlene
. venvname/bin/activate
```

### To use, permanently
```
pip3 install --break-system-packages --user Lurlene
```
See `~/.local/bin` for executables.

### To develop
First install venvpool to get the `motivate` command:
```
pip3 install --break-system-packages --user venvpool
```
Get codebase and install executables:
```
git clone git@github.com:combatopera/Lurlene.git
motivate Lurlene
```
Requirements will be satisfied just in time, using sibling projects with matching .egg-info if any.

## API

<a id="lurlene"></a>

### lurlene

<a id="lurlene.api"></a>

### lurlene.api

<a id="lurlene.pitch"></a>

### lurlene.pitch

<a id="lurlene.scale"></a>

### lurlene.scale

