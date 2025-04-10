import datetime
import argparse
import math
from termcolor import colored
import os
import subprocess
import wand.image
from wand.api import library
from ctypes import c_void_p, c_size_t
from wand_utils import get_bytes_per_channel

start_datetime = datetime.datetime.now()

parser = argparse.ArgumentParser(
    prog="autoscale",
    description="Resizes an image to the maximum size to run upscayl on"
)
parser.add_argument("filename", help="Input File")
parser.add_argument("-f", "--scale-factor", help="Desired enlargement factor (default=4)", type=float, default=4.0, required=False)
parser.add_argument("-sr", "--sharpen-radius", help="Sharpen radius (default=0.8)", type=float, default=0.8, required=False)
parser.add_argument("-ss", "--sharpen-sigma", help="Sharpen sigma (default=33)", type=float, default=33.0, required=False)
parser.add_argument('--no-auto-upscayl', action="store_true", help="Disables the automatic upscaling using upscayl (requires upscayl-bin in PATH)")
parser.add_argument("-m", "--upscayl-model", help="Select the upscayl model (default=digital-art-4x)", type=str, default="digital-art-4x", required=False)
parser.add_argument("-ttap", "--upscayl-enable-tta-pre", action="store_true", help="Enable TTA mode for pre-upscayle")
parser.add_argument("-ttaf", "--upscayl-enable-tta-fin", action="store_true", help="Enable TTA mode for final upscayl")
parser.add_argument("-uv", "--upscayl-verbose", action="store_true", help="Enables the output of Upscayl")
parser.add_argument("--no-jpegli", action="store_true", help="Disables the automatic recompressing using JPEGLI (requires cjpegli to be in PATH)")
parser.add_argument("-jq", "--jpegli-quality", help="JPEGLI quality setting (default=84)", type=str, default=84, required=False)
parser.add_argument("-jp", "--jpegli-progressive", help="JPEGLI progressive mode (default=0)", type=str, default=0, required=False)
parser.add_argument("-jy", "--jpegli-yuv-format", help="JPEGLI YUV format (default=420)", type=str, default="420", required=False)
parser.add_argument("-jv", "--jpegli-verbose", action="store_true", help="Enables the output of cjpegli")
args = parser.parse_args()
parsed_args_dict = vars(args)

# Print args
print(colored("Autoscale for upscayl! ==== ", 'light_cyan') + colored(f"START: {start_datetime} ", 'light_yellow') + colored("=================", 'light_cyan'))
print("=> Parameters used:")
for key, value in parsed_args_dict.items():
    key = key.upper()
    print(f"{key:>24}: {value}")
print("")

# Tell Python's wand library about the MagickWand Compression Quality (not Image's Compression Quality)
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]

# Maximum size Upscayl currently supports
maxSz = pow(2,31)-1

# Load image
img = wand.image.Image(filename=args.filename)
bpp = get_bytes_per_channel(img)

if img.alpha_channel == False:
    img_alpha = "No Alpha"
else:
    img_alpha = "Alpha"
print(f"=> Image loaded: {img.format} / {img.width} x {img.height} / {bpp*8}bpp / {img.colorspace.upper()} / {img_alpha}")


had_alpha = False
# If this image has an alpha channel, remove it
if img.alpha_channel != False:
    img.background_color = wand.image.Color('black')
    img.alpha_channel = 'remove'
    had_alpha = True
    print("=> Removed alpha channel")

#Determine new width and height
bpp = get_bytes_per_channel(img)
w = 0
h = 0
f = args.scale_factor
a = img.width/img.height

while ((w+1)*f*((w+1)/a)*f*bpp<=maxSz):
    w+=1
    h=w/a

w=math.floor(w)
h=math.floor(h)

print(f"=> Determined new width and height: {w} x {h}, final size will be {w*4} x {h*4}")

ow = img.width
oh = img.height

ret_code = 999999
if w*h>ow*oh:
    print(colored("/!\ Input image is too small, it needs to be upscaled first.", 'light_yellow'))
    if args.no_auto_upscayl == False:
        uifn = args.filename
        uofn = args.filename.rpartition('.')[0] + '_utmp2.png'

        # Save temp image when alpha has previously been removed
        if had_alpha:
            img.strip()
            uifn = args.filename.rpartition('.')[0] + "_utmp0.png"
            img.save(filename=uifn)

        # Free memory
        img.close()
        img.destroy()

        # Prepare upscayl loop
        print("=> Starting Upscayl...")

        # Determine iterations. I am bad at math, so I use a loop
        iterations=0
        tow=ow
        toh=oh
        while tow*toh < w*h:
            tow*=f
            toh*=f
            iterations+=1

        print(f"(i) Upscayl iterations needed: {iterations}")

        if iterations > 3:
            print(colored("(x) More than 3 upscayl iterations required. This is not advisable. Aborting...", 'light_red'))
            os._exit(0x128)

        for i in range(1, iterations+1):
            print(f"=> Running Upscayl iteration {i}...")
            uofn = args.filename.rpartition('.')[0] + f'_utmp{i}.png'
            if args.upscayl_enable_tta_pre:
                ucmd = f"upscayl-bin -i \"{uifn}\" -o \"{uofn}\" -m \"..\\models\" -n {args.upscayl_model} -s {f} -c 1 -x"
            else:
                ucmd = f"upscayl-bin -i \"{uifn}\" -o \"{uofn}\" -m \"..\\models\" -n {args.upscayl_model} -s {f} -c 1"
            if args.upscayl_verbose == False:
                with open(os.devnull, 'w') as fnull:
                    ret_code = subprocess.call(ucmd, shell=True, stdout=fnull, stderr=fnull)
            else:
                ret_code = subprocess.call(ucmd, shell=True)
            if ret_code == 0:
                if i > 1 or had_alpha:
                    os.remove(uifn)
                uifn = uofn
            else:
                print(colored(f"(x) Upscayl error! Command: {ucmd}", 'light_red'))
                os._exit(0x129)

        if ret_code == 0:
            img = wand.image.Image(filename=uofn)
            print(f"=> Upscayled Image loaded: {img.format} / {img.width} x {img.height} / {bpp*8}bpp / {img.colorspace.upper()} / No Alpha")
            os.remove(uifn)
        else:
            print(colored(f"(x) Unknown error!", 'light_red'))
            os._exit(0x129)
    else:
        print(colored("(x) No upscaling using AI selected, script will exit with an error.", 'light_red'))
        os._exit(0x127)

#Scale image
img.resize(w, h, 'triangle')
print("=> Scaled image")
if args.sharpen_sigma != 0 and args.sharpen_radius != 0:
    img.sharpen(args.sharpen_radius, args.sharpen_sigma)
    print("=> Sharpened image")

print("=> Saving as PNG with fast compression...")
#Save
library.MagickSetCompressionQuality(img.wand, 10)
img.strip()
img.save(filename=args.filename.rpartition('.')[0] + '_tmp.png')
img.close()
img.destroy()

#Last upscayl step
print(f"=> Upscayling to maximum size of {w*4} x {h*4}...")
uifn = args.filename.rpartition('.')[0] + '_tmp.png'
uofn = args.filename.rpartition('.')[0] + '_upscayl.png'
if args.upscayl_enable_tta_fin:
    ucmd = f"upscayl-bin -i \"{uifn}\" -o \"{uofn}\" -m \"..\\models\" -n {args.upscayl_model} -s {f} -c 1 -x"
else:
    ucmd = f"upscayl-bin -i \"{uifn}\" -o \"{uofn}\" -m \"..\\models\" -n {args.upscayl_model} -s {f} -c 1"
    if args.upscayl_verbose == False:
        with open(os.devnull, 'w') as fnull:
            ret_code = subprocess.call(ucmd, shell=True, stdout=fnull, stderr=fnull)
    else:
        ret_code = subprocess.call(ucmd, shell=True)
if ret_code == 0:
    os.remove(uifn)
else:
    print(colored(f"(x) Upscayl error! Command: {ucmd}", 'light_red'))
    os._exit(0x129)
print(f"=> Written {uofn}")

# If desired, compress the resulting PNG with JPEGLI and delete the huge PNG file afterwards
if args.no_jpegli == False:
    print(f"=> Recompressing the PNG with JPEGLI...")
    jifn = uofn
    jofn = args.filename.rpartition('.')[0] + '_upscayl.jpg'
    jcmd = f"cjpegli -q {args.jpegli_quality} -p {args.jpegli_progressive} --chroma_subsampling={args.jpegli_yuv_format} \"{jifn}\" \"{jofn}\""
    if args.jpegli_verbose == False:
        with open(os.devnull, 'w') as fnull:
            ret_code = subprocess.call(jcmd, shell=True, stdout=fnull, stderr=fnull)
    else:
        ret_code = subprocess.call(jcmd, shell=True)
    if ret_code == 0:
        os.remove(jifn)
    else:
        print(colored(f"(x) JPEGLI error! Command: {jcmd}", 'light_red'))
        os._exit(0x126)

datetime_end = datetime.datetime.now()
print(colored(f"END ..... : {datetime_end}", 'light_green'))
print(colored(f"TIME TAKEN: {datetime_end - start_datetime}", 'light_green'))
print(colored("Finished.", 'light_green'))
