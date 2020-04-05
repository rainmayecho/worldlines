# worldlines
GIF to Toroidal worldlines

## Requirements

```bash
brew install libagg pkg-config potrace

[in project root]
. env/bin/activate
pip install -r requirements.txt
```

## Usage
#### Building SVG Sequence
Converts a .gif into multiple svg frames. It works best if the gif is already greyscale & contains hard boundaries.
```bash
[in project root]
. env/bin/activate
cd src
python trace.py -i <path or glob expr>.gif
```
This also prints to `stdout` some OpenSCAD code to generate a toroid from the output svg files.

#### Cleaning converted directory
```bash
[in project root]
. env/bin/activate
cd src
python trace.py -c 1
```
