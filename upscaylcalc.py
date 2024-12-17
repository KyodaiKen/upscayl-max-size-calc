import argparse
import math

parser = argparse.ArgumentParser(
    prog="upscaylcalc",
    description="Calculates the maximum size for upscayl to be able to upscayl"
)
parser.add_argument("-iw", help="Input width", type=int, required=True)
parser.add_argument("-ih", help="Input height", type=int, required=True)
parser.add_argument("-bpp", help="Bits per pixel (default=24)", type=int, default=24, required=False)
parser.add_argument("-f", help="Desired enlargement factor (default=4)", type=float, default=4.0, required=False)
args = parser.parse_args()

maxSz = pow(2,31)-1

w = 0
h = 0
f = args.f
a = args.iw/args.ih
bpp = args.bpp/8

while ((w+1)*f*((w+1)/a)*f*bpp<=maxSz):
    w+=1
    h=w/a

w=math.floor(w)
h=math.floor(h)

print("INPUT ---------------------")
print("width .... :",int(w))
print("height ... :",int(h))
print("megapixels :",round(w*h/pow(10,6),3))
print()
print("scale .... :", f, "x")
print("bpp ...... :", int(bpp*8), "bit")
print()
print("AFTER UPSCAYLING ----------")
print("width .... :",int(w*f))
print("height ... :",int(h*f))
print("megapixels :",round(w*f*h*f/pow(10,6),3))
print("max mpx .. :",round(maxSz/bpp/pow(10,6),3))
print("loss ..... :",round(100-(w*f*h*f)/(maxSz/bpp)*100,3),"percent")