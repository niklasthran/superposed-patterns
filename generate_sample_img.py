# generate_sample_img.py
# GENERATE SAMPLE IMG

# -----------------------------------------------------------------------------------
# INCLUDE ALL MODULES
# -----------------------------------------------------------------------------------

# PILlow for image generation
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

# Command line arguments parsing
import argparse

# For saving files in current directory
import os

# -----------------------------------------------------------------------------------
# DEFINE ALL FUNCTIONS
# -----------------------------------------------------------------------------------

# Base funtions

def lin_map(x, in_min, in_max, out_min, out_max):
    if in_min == in_max:
        return out_max / 2
    else:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def step(x, w, out_min, out_max):
    if x < w / 2:
        return out_min
    if x >= w / 2:
        return out_max

def step_div(x, y, w, out_min, out_max):
    if x < w / 2 and y < w / 2 or x >= w / 2 and y >= w / 2:
        return out_max
    if x < w / 2 and y >= w / 2 or x >= w / 2 and y < w / 2:
        return out_min

def dist(x, y):
    return (x - (y - 1) / 2) ** 2

# -----------------------------------------------------------------------------------

# Generate sample images using base functions above

# Linear interpolation, orthogonal

def cont_interp_orth(a, path):
    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            c = int(lin_map(i, 0, a, 0, 255))
            img.putpixel((i, j), (c, c, c))

    #img.show()
    img.save(f'{path}/sample_cont_interp_orth_0_{a}x{a}px.png')
    img = img.rotate(90)
    img.save(f'{path}/sample_cont_interp_orth_90_{a}x{a}px.png')
    img = img.rotate(180)
    img.save(f'{path}/sample_cont_interp_orth_180_{a}x{a}px.png')
    img = img.rotate(270)
    img.save(f'{path}/sample_cont_interp_orth_270_{a}x{a}px.png')

# -----------------------------------------------------------------------------------

# Linear interpolation diagonal

def cont_interp_dia(a, path):
    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            c = int(lin_map((i + j) / 2, 0, a, 0, 255))
            img.putpixel((i, j), (c, c, c))

    #img.show()
    img.save(f'{path}/sample_cont_interp_dia_0_{a}x{a}px.png')
    img = img.rotate(90)
    img.save(f'{path}/sample_cont_interp_dia_90_{a}x{a}px.png')
    img = img.rotate(180)
    img.save(f'{path}/sample_cont_interp_dia_180_{a}x{a}px.png')
    img = img.rotate(270)
    img.save(f'{path}/sample_cont_interp_dia_270_{a}x{a}px.png')

# -----------------------------------------------------------------------------------

# Radial gradient

def cont_interp_rad(a, path):
    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            d = lin_map(dist(i, a) + dist(j, a), dist(a / 2, a) * 2, dist(0, a) * 2, 0, 1)
            d = d ** (1 / 2)
            color = int(d * 255)
            img.putpixel((i, j), (color, color, color))

    #img.show()
    img.save(f'{path}/sample_cont_interp_rad_{a}x{a}px.png')
    img = ImageOps.invert(img)
    img.save(f'{path}/sample_cont_interp_rad_inv_{a}x{a}px.png')

# -----------------------------------------------------------------------------------

# Step orthogonal

def disc_orth(a, path):
    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            c = int(step(i, a, 0, 255))
            img.putpixel((i, j), (c, c, c))

    #img.show()
    img.save(f'{path}/sample_disc_orth_0_{a}x{a}px.png')
    img = img.rotate(90)
    img.save(f'{path}/sample_disc_orth_90_{a}x{a}px.png')
    img = img.rotate(180)
    img.save(f'{path}/sample_disc_orth_180_{a}x{a}px.png')
    img = img.rotate(270)
    img.save(f'{path}/sample_disc_orth_270_{a}x{a}px.png')

# -----------------------------------------------------------------------------------

# Step diagonal

def disc_dia(a, path):
    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            c = int(step((i + j) / 2, a, 0, 255))
            img.putpixel((i, j), (c, c, c))

    #img.show()
    img.save(f'{path}/sample_disc_dia_0_{a}x{a}px.png')
    img = img.rotate(90)
    img.save(f'{path}/sample_disc_dia_90_{a}x{a}px.png')
    img = img.rotate(180)
    img.save(f'{path}/sample_disc_dia_180_{a}x{a}px.png')
    img = img.rotate(270)
    img.save(f'{path}/sample_disc_dia_270_{a}x{a}px.png')

# -----------------------------------------------------------------------------------

# Checkerboard pattern

def disc_checker(a, path):
    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            c = int(step_div(i, j, a, 0, 255))
            img.putpixel((i, j), (c, c, c))

    #img.show()
    img.save(f'{path}/sample_disc_checker_0_{a}x{a}px.png')
    img = img.rotate(90)
    img.save(f'{path}/sample_disc_checker_90_{a}x{a}px.png')

# -----------------------------------------------------------------------------------

# Alphanumeric

def alphanum(txt, a, path):
    font = ImageFont.truetype("Inter-Regular.ttf", a)

    img = Image.new('RGB', (a, a))
    for i in range(a):
        for j in range(a):
            c = 255
            img.putpixel((i, j), (c, c, c))

    draw = ImageDraw.Draw(img)
    draw.text(((a/2) - (font.getbbox(txt)[2]/2), (a/2) - ((font.getbbox(txt)[1] + font.getbbox(txt)[3])/2)), txt, (0, 0, 0), font)

    #img.show()
    img.save(f'{path}/sample_alphanum_{txt}_{a}x{a}px.png')
    img = ImageOps.invert(img)
    img.save(f'{path}/sample_alphanum_{txt}_inv_{a}x{a}px.png')

# -----------------------------------------------------------------------------------
# CALL FUNCTIONS ACCORDING TO ARGUMENTS
# -----------------------------------------------------------------------------------

# Argument parsing from command line
parser = argparse.ArgumentParser(
    description =   '''
                    Use this piece of software to automatically
                    create an array of different sample images
                    to test in experiment3.py. 
                    ''',
    epilog      =   '''
                    Your created sample images will
                    be filed in a directory that sits
                    in the same place as this program.
                    ''')

parser.add_argument('--sidelength',
    type        =   int,
    required    =   True,
    help        =   '''
                    Specify a common side length of the
                    sample images as an integer such as 4.
                    ''')

args = parser.parse_args()

# Create directory for output images
out_dir = 'sample_img'
path = os.path.join(os.getcwd(), out_dir)
try:
    os.mkdir(path)

# Make sure directory does not get overwritten
except FileExistsError:
    pass

# -----------------------------------------------------------------------------------

# Generate images

a = args.sidelength

# Create directory for each size
path = os.path.join(path, f"{a}x{a}")
try:
    os.mkdir(path)

# Make sure directory does not get overwritten
except FileExistsError:
    pass

# Discrete
disc_orth(a, path)
disc_dia(a, path)
disc_checker(a, path)

# Continuous
cont_interp_orth(a, path)
cont_interp_dia(a, path)
cont_interp_rad(a, path)

# Alphanumeric
alphanum("A", a, path)