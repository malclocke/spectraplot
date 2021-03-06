#! /usr/bin/env python
import specreduce
import argparse
import pyfits
import matplotlib.pyplot as plt
import numpy as np

element_lines = {
  'Ha': specreduce.ElementLine(6563, r'H$\alpha$'),
  'Hb': specreduce.ElementLine(4861, r'H$\beta$'),
  'Hg': specreduce.ElementLine(4341, r'H$\gamma$'),
  'Hd': specreduce.ElementLine(4102, r'H$\delta$'),
  'CaH': specreduce.ElementLine(3968, 'Ca H'),
  'CaK': specreduce.ElementLine(3934, 'Ca K'),
}

# These linestyles are used for grayscale plots.
dashes = [ '-', '--', '-.', ':' ]

def get_spectra(filename, legend_keyword = 'DATE-OBS'):
  hdulist = pyfits.open(filename)

  if hdulist[0].header['NAXIS'] == 1:
    s = specreduce.BessSpectra(hdulist)
  else:
    s = specreduce.ImageSpectra(hdulist[0].data)

  s.set_label_header(legend_keyword)
  return s


def get_line(line_definition):
  if ":" in line_definition:
    wavelength, label = line_definition.split(":")
    return specreduce.ElementLine(float(wavelength), label)
  else:
    return element_lines[line_definition]

def calibration_reference_from_arg(arg):
  pixel, angstrom = arg.split(':')

  if angstrom in element_lines:
    angstrom = element_lines[angstrom].angstrom

  return specreduce.CalibrationReference(float(pixel), float(angstrom))


parser = argparse.ArgumentParser(description='Plot spectra')
parser.add_argument('filename', type=str, help='FITS filename',
    nargs='+')
parser.add_argument('--calibrate', '-c', dest='calibration', type=str,
    help='Calibration pixel position.  Format pixel:angstrom,pixel:angstrom or pixel,angstrom,angstrom_per_pixel')
parser.add_argument('--lines', '-l', dest='lines', type=str,
                    help='Plot specified lines.')
parser.add_argument('--title', '-t', dest='title', type=str, help='Plot title')
parser.add_argument('--suptitle', '-s', dest='suptitle', type=str, help='Plot super-title, appears above title')
parser.add_argument('--listlines', '-L', action='store_true',
    help='List available lines')
parser.add_argument('--crop', '-C', action='store_true', help='Crop spectra')
parser.add_argument('--croprange', type=str, default='3900:7000',
    help='Set crop range (default: 3900:7000)')
parser.add_argument('--headerlabel', '-H', type=str, default='DATE-OBS',
    help='Use the value of the specified FITS header as the legend (default: DATE-OBS)')
parser.add_argument('--offset', '-o', type=float, default=0.0,
    help='Offset each plot by offset in the Y axes.  Default: 0.0')
parser.add_argument('--grayscale', '-g', action='store_true',
    help='Plot chart grayscale')


args = parser.parse_args()

if args.listlines:
  for k, v in element_lines.iteritems():
    print "%4s %s" % (k, v)
  exit()

base_spectra = get_spectra(args.filename[0], args.headerlabel)

if base_spectra.can_plot_image:
  graph_subplot = plt.subplot(211)
  image_subplot = plt.subplot(212)
  image_subplot.set_xlabel('x px')
  image_subplot.set_ylabel('y px')
  base_spectra.plot_image_onto(image_subplot)
else:
  graph_subplot = plt.subplot(111)

if args.crop:
  crop_left, crop_right = args.croprange.split(':')
  graph_subplot.set_xlim(left=int(crop_left),right=int(crop_right))

graph_subplot.set_ylabel('Relative intensity')

plots = []
plots.append(base_spectra)

if args.calibration:
  calibration_elements = args.calibration.split(',')

  if ':' in args.calibration:
    if len(calibration_elements) == 2:
      calibration = specreduce.DoublePointCalibration(
        calibration_reference_from_arg(calibration_elements[0]),
        calibration_reference_from_arg(calibration_elements[1])
      )
    elif len(calibration_elements) > 2:
      references = []
      for element in calibration_elements:
        references.append(calibration_reference_from_arg(element))
      calibration = specreduce.NonLinearCalibration(references)
    else:
      raise ValueError('Unable to parse calibration argument')
  elif len(calibration_elements) == 3:
    pixel, angstrom, angstrom_per_pixel = calibration_elements
    if angstrom in element_lines:
      angstrom = element_lines[angstrom].angstrom
    calibration = specreduce.SinglePointCalibration(
      specreduce.CalibrationReference(float(pixel), float(angstrom)),
      float(angstrom_per_pixel)
    )
  else:
    raise ValueError('Unable to parse calibration argument')

  base_spectra.set_calibration(calibration)

if base_spectra.calibration:

  print base_spectra.calibration

  if args.lines:
    lines_to_plot = args.lines.split(',')

    for line_to_plot in lines_to_plot:
      line = get_line(line_to_plot)
      plots.append(line)

  graph_subplot.axvline(x=0, color='yellow')
  graph_subplot.set_xlabel(r'Wavelength ($\AA$)')

else:
  graph_subplot.set_xlabel('Pixel')
  

if args.title:
  title = args.title
else:
  title = args.filename[0]

plt.title(title)

if args.suptitle:
  plt.suptitle(args.suptitle)

if len(args.filename) > 1:
  [plots.append(get_spectra(s, args.headerlabel)) for s in args.filename[1:]]

for i, plot in enumerate(plots):
  offset = args.offset * (len(plots) - i)
  plot.grayscale = args.grayscale
  if args.grayscale:
    plot.linestyle = dashes[np.mod(i, len(dashes))]

  plot.plot_onto(graph_subplot, offset = offset)

graph_subplot.legend(loc='best')

plt.show()
