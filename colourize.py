#! /usr/bin/env python

from PIL import Image
import numpy as np
import pyfits
import specreduce
import argparse


def wav2RGB(wavelength, intensity):
  w = int(wavelength)

  # colour
  if w >= 380 and w < 440:
    R = -(w - 440.) / (440. - 350.)
    G = 0.0
    B = 1.0
  elif w >= 440 and w < 490:
    R = 0.0
    G = (w - 440.) / (490. - 440.)
    B = 1.0
  elif w >= 490 and w < 510:
    R = 0.0
    G = 1.0
    B = -(w - 510.) / (510. - 490.)
  elif w >= 510 and w < 580:
    R = (w - 510.) / (580. - 510.)
    G = 1.0
    B = 0.0
  elif w >= 580 and w < 645:
    R = 1.0
    G = -(w - 645.) / (645. - 580.)
    B = 0.0
  elif w >= 645 and w <= 780:
    R = 1.0
    G = 0.0
    B = 0.0
  else:
    R = 1.0
    G = 1.0
    B = 1.0

  # intensity correction
  if w >= 380 and w < 420:
    SSS = 0.3 + 0.7*(w - 350) / (420 - 350)
  elif w >= 420 and w <= 700:
    SSS = 1.0
  elif w > 700 and w <= 780:
    SSS = 0.3 + 0.7*(780 - w) / (780 - 700)
  else:
    SSS = 1.0

  SSS *= 255
  SSS *= intensity

  return (int(SSS*R), int(SSS*G), int(SSS*B))

def angstrom2RGB(angstrom, intensity):
  return wav2RGB(angstrom/10, intensity)

def intensity2RGB(intensity):
  value = int(intensity * 255)
  return (value, value, value)

parser = argparse.ArgumentParser(description='Create a color image from a FITS spectra')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--height', '-y', type=int, default=50, help='Image height')
parser.add_argument('--outfile', '-o', type=str)
parser.add_argument('--greyscale', '-g', action='store_true',
    help='Output a greyscale image')
parser.add_argument('--split', '-s', action='store_true',
    help='Make the image split half colour, half greyscale')
parser.add_argument('--graph', '-G', action='store_true',
    help='Overlay an intensity graph on the image')

args = parser.parse_args()

spectra = specreduce.BessSpectra(pyfits.open(args.filename))

wavelengths = spectra.wavelengths()
data = spectra.data()
max_value = data.max()
width = len(wavelengths)
height = args.height
image = Image.new('RGB', (width, height), 'black')
pixels = image.load()

for y in range(0, height):
  for x in range(0, width):
    scaled_y = int(data[x] / (float(max_value) / height))
    if args.graph and height - y == scaled_y:
      pixels[x,y] = (255,255,255)
    elif args.greyscale:
      pixels[x,y] = intensity2RGB(float(data[x]) / max_value)
    elif args.split and y > height / 2:
      pixels[x,y] = intensity2RGB(float(data[x]) / max_value)
    else:
      pixels[x,y] = angstrom2RGB(wavelengths[x], float(data[x]) / max_value)

if args.outfile:
  image.save(args.outfile)
else:
  image.show()
