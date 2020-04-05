from itertools import chain
from collections import deque
from PIL import Image
from potrace import Bitmap  # pylint: disable=no-name-in-module

import argparse
import ffmpeg
import glob
import os
import numpy as np
import subprocess
import sys

CONVERTED_DIR = "images/converted"
BMP_SUFFIX = "converted_%2d.bmp"

reduce_pixels = np.vectorize(lambda x: 1 - int(bool(255 - x)))


def exhaust(generator):
    return deque(generator, maxlen=0)

def gif_to_bmp(gen):
    for filename in gen:
        prefix = filename.split("/")[-1].split(".")[0]
        outfile = f"{CONVERTED_DIR}/{prefix}_{BMP_SUFFIX}"
        ffmpeg.input(filename).output(outfile).run()
        yield f"{CONVERTED_DIR}/{prefix}"

def bmp_to_svg(gen):
    for expression in gen:
        for filename in glob.glob(f"{expression}*.bmp"):
            outfile = f"{CONVERTED_DIR}/{filename.split('/')[-1].split('.')[0]}.svg"
            subprocess.call([
                "potrace",
                "-s",
                filename,
                "-o",
                outfile
            ])
            yield outfile
        

def iterfiles(_globs):
    for expression in _globs:
        for filename in glob.glob(expression, recursive=True):
            yield filename

def main(_globs):
    file_expressions = gif_to_bmp(iterfiles(_globs))
    svg_files = [f for f in bmp_to_svg(file_expressions)]
    gen_openscad_code(svg_files)

def clean():
    for file in glob.glob(f"{CONVERTED_DIR}/*"):
        os.remove(file)

def numerical_sort_key(path):
    return int(path.split("/")[-1].split(".")[0].split("_")[-1])

def gen_openscad_code(svg_files):
    n_files = len(svg_files)
    prefix = os.path.abspath(f".")
    files = ',\n\t\t'.join(f'"{prefix}/{f}"' for f in sorted(svg_files, key=numerical_sort_key))
    code = f"""
    $r = 75;
    $ds = 360 / {n_files};

    $files = [
        {files}
    ];

    for(i = [0 : {n_files}]) {{
        translate([$r * cos($ds * i), 0, -$r * sin($ds * i)])
        rotate($ds * i, [0, 1, 0])
        import($files[i]);
    }}
    """
    print(code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="A glob expression of input files")
    parser.add_argument("-c", "--clean", help="Cleans the converted directory")
    args = parser.parse_args()
    if args.clean:
        clean()
    else:
        main(args.input.split(" "))
    