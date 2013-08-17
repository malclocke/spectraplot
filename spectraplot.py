#! /usr/bin/env python
import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
import argparse
import os


class CalibrationReference:
  def __init__(self, pixel, angstrom):
    self.pixel = pixel
    self.angstrom = angstrom

class Calibration:
  def __init__(self, reference1, reference2):
    self.reference1 = reference1
    self.reference2 = reference2

  def __repr__(self):
    return "<Calibration angstrom_per_pixel: %f>" % (
        self.angstrom_per_pixel()
    )

  def angstrom(self, pixel):
    return (self.slope() * (pixel - self.reference1.pixel)) + self.reference1.angstrom

  def slope(self):
    return self.angstrom_difference() / self.pixel_difference()

  def angstrom_difference(self):
    return self.reference1.angstrom - self.reference2.angstrom

  def pixel_difference(self):
    return self.reference1.pixel - self.reference2.pixel

  def angstrom_per_pixel(self):
    return self.slope()



class ElementLine:
  def __init__(self, angstrom, label):
    self.angstrom = angstrom
    self.label = label

  def __repr__(self):
    return "%f (%s)" % (self.angstrom, self.label)

  def color(self):
    return 'red'

  def plot_label(self):
    return '%s (%.02f $\AA$)' % (self.label, self.angstrom)

  def plot_onto(self, axes):
    axes.axvline(x=self.angstrom, color=self.color())
    axes.text(self.angstrom, 10, self.plot_label(),
        rotation='vertical', verticalalignment='bottom')


class Reference:

  references = {
    "M5III": "pickles_100.fits", "M6III": "pickles_101.fits",
    "M7III": "pickles_102.fits", "M8III": "pickles_103.fits",
    "M9III": "pickles_104.fits", "M10III": "pickles_105.fits",
    "B2II": "pickles_106.fits", "B5II": "pickles_107.fits",
    "F0II": "pickles_108.fits", "F2II": "pickles_109.fits",
    "A2V": "pickles_10.fits", "G5II": "pickles_110.fits",
    "K01II": "pickles_111.fits", "K34II": "pickles_112.fits",
    "M3II": "pickles_113.fits", "B0I": "pickles_114.fits",
    "B1I": "pickles_115.fits", "B3I": "pickles_116.fits",
    "B5I": "pickles_117.fits", "B8I": "pickles_118.fits",
    "A0I": "pickles_119.fits", "A3V": "pickles_11.fits",
    "A2I": "pickles_120.fits", "F0I": "pickles_121.fits",
    "F5I": "pickles_122.fits", "F8I": "pickles_123.fits",
    "G0I": "pickles_124.fits", "G2I": "pickles_125.fits",
    "G5I": "pickles_126.fits", "G8I": "pickles_127.fits",
    "K2I": "pickles_128.fits", "K3I": "pickles_129.fits",
    "A5V": "pickles_12.fits", "K4I": "pickles_130.fits",
    "M2I": "pickles_131.fits", "A7V": "pickles_13.fits",
    "F0V": "pickles_14.fits", "F2V": "pickles_15.fits",
    "F5V": "pickles_16.fits", "F5V": "pickles_17.fits",
    "F6V": "pickles_18.fits", "F6V": "pickles_19.fits",
    "O5V": "pickles_1.fits", "F8V": "pickles_20.fits",
    "F8V": "pickles_21.fits", "F8V": "pickles_22.fits",
    "G0V": "pickles_23.fits", "G0V": "pickles_24.fits",
    "G0V": "pickles_25.fits", "G2V": "pickles_26.fits",
    "G5V": "pickles_27.fits", "G5V": "pickles_28.fits",
    "G5V": "pickles_29.fits", "O9V": "pickles_2.fits",
    "G8V": "pickles_30.fits", "K0V": "pickles_31.fits",
    "K0V": "pickles_32.fits", "K2V": "pickles_33.fits",
    "K3V": "pickles_34.fits", "K4V": "pickles_35.fits",
    "K5V": "pickles_36.fits", "K7V": "pickles_37.fits",
    "M0V": "pickles_38.fits", "M1V": "pickles_39.fits",
    "B0V": "pickles_3.fits", "M2V": "pickles_40.fits",
    "M2.5V": "pickles_41.fits", "M3V": "pickles_42.fits",
    "M4V": "pickles_43.fits", "M5V": "pickles_44.fits",
    "M6V": "pickles_45.fits", "B2IV": "pickles_46.fits",
    "B6IV": "pickles_47.fits", "A0IV": "pickles_48.fits",
    "A47IV": "pickles_49.fits", "B1V": "pickles_4.fits",
    "F02IV": "pickles_50.fits", "F5IV": "pickles_51.fits",
    "F8IV": "pickles_52.fits", "G0IV": "pickles_53.fits",
    "G2IV": "pickles_54.fits", "G5IV": "pickles_55.fits",
    "G8IV": "pickles_56.fits", "K0IV": "pickles_57.fits",
    "K1IV": "pickles_58.fits", "K3IV": "pickles_59.fits",
    "B3V": "pickles_5.fits", "O8III": "pickles_60.fits",
    "B12III": "pickles_61.fits", "B3III": "pickles_62.fits",
    "B5III": "pickles_63.fits", "B9III": "pickles_64.fits",
    "A0III": "pickles_65.fits", "A3III": "pickles_66.fits",
    "A5III": "pickles_67.fits", "A7III": "pickles_68.fits",
    "F0III": "pickles_69.fits", "B57V": "pickles_6.fits",
    "F2III": "pickles_70.fits", "F5III": "pickles_71.fits",
    "G0III": "pickles_72.fits", "G5III": "pickles_73.fits",
    "G5III": "pickles_74.fits", "G5III": "pickles_75.fits",
    "G8III": "pickles_76.fits", "G8III": "pickles_77.fits",
    "K0III": "pickles_78.fits", "K0III": "pickles_79.fits",
    "B8V": "pickles_7.fits", "K0III": "pickles_80.fits",
    "K1III": "pickles_81.fits", "K1III": "pickles_82.fits",
    "K1III": "pickles_83.fits", "K2III": "pickles_84.fits",
    "K2III": "pickles_85.fits", "K2III": "pickles_86.fits",
    "K3III": "pickles_87.fits", "K3III": "pickles_88.fits",
    "K3III": "pickles_89.fits", "B9V": "pickles_8.fits",
    "K4III": "pickles_90.fits", "K4III": "pickles_91.fits",
    "K4III": "pickles_92.fits", "K5III": "pickles_93.fits",
    "K5III": "pickles_94.fits", "M0III": "pickles_95.fits",
    "M1III": "pickles_96.fits", "M2III": "pickles_97.fits",
    "M3III": "pickles_98.fits", "M4III": "pickles_99.fits",
    "A0V": "pickles_9.fits",
  }
  base_path = os.path.dirname(os.path.realpath(__file__))
  subdir = "ftp.stsci.edu/cdbs/grid/pickles/dat_uvi/"
  scale_factor = 1

  def __init__(self, reference, interpolate_source=False):
    self.hdulist = pyfits.open(self.reference_path(reference))
    self.label = 'Reference (%s)' % reference
    self.interpolate_source = interpolate_source

  def wavelengths(self):
    return self.hdulist[1].data.field(0)

  def interp(self, target_wavelengths, target_intensities):
    return np.interp(
        target_wavelengths, self.wavelengths(), self.data()
    )

  def interpolate_to(self, spectra):
    return self.interp(spectra.wavelengths(), spectra.data())

  def scale_to(self, spectra):
    self.scale_factor = spectra.max() / self.data().max()
    return self.scale_factor

  def reference_path(self, reference):
    return os.path.join(self.pickles_dir(), self.references[reference])

  def pickles_dir(self):
    return os.path.join(self.base_path, self.subdir)

  def data(self):
    return self.scale_factor * self.hdulist[1].data.field(1)

  def plot_onto(self, axes):
    axes.plot(self.wavelengths(), self.data(), label=self.label)


class ImageSpectra:

  label = 'Raw data'
  calibration = False

  def __init__(self, data):
    self.raw = data

  def data(self):
    return self.raw.sum(axis=0)

  def set_calibration(self, calibration):
    self.calibration = calibration

  def wavelengths(self):
    if self.calibration:
      return [self.calibration.angstrom(i) for i in range(len(self.data()))]
    else:
      return range(len(self.data()))

  def plot_image_onto(self, axes):
    imgplot = axes.imshow(self.raw)
    imgplot.set_cmap('gray')

  def plot_onto(self, axes):
    axes.plot(self.wavelengths(), self.data(), label=self.label)

  def divide_by(self, other_spectra):
    divided = np.divide(self.data(), other_spectra.interpolate_to(self))
    divided[divided==np.inf]=0
    return divided

  def max(self):
    return self.data().max()

class CorrectedSpectra:

  smoothing = 20
  spacing   = 500
  k         = 1
  label     = 'Corrected'

  def __init__(self, uncorrected, reference):
    self.uncorrected = uncorrected
    self.reference = reference

  def wavelengths(self):
    return self.uncorrected.wavelengths()

  def divided(self):
    return self.uncorrected.divide_by(self.reference)

  def plot_onto(self, axes):
    axes.plot(self.wavelengths(), self.data(), label=self.label)

  def data(self):
    return np.divide(self.uncorrected.data(), self.smoothed())

  def smoothed(self):
    tck = scipy.interpolate.splrep(
      self.wavelengths(), self.divided(), s=self.smoothing, k=self.k
    )
    return scipy.interpolate.splev(self.wavelengths(), tck)



def main():
  element_lines = {
    'Ha': ElementLine(6563, r'H$\alpha$'),
    'Hb': ElementLine(4861, r'H$\beta$'),
    'Hg': ElementLine(4341, r'H$\gamma$'),
    'Hd': ElementLine(4102, r'H$\delta$'),
    'CaH': ElementLine(3968, 'Ca H'),
    'CaK': ElementLine(3934, 'Ca K'),
  }

  parser = argparse.ArgumentParser(description='Process linear SA100 spectra')
  parser.add_argument('filename', type=str, help='FITS filename')
  parser.add_argument('--calibration', '-c', dest='calibration', type=str,
      help='Calibration pixel position.  Format pixel:angstrom,pixel:angstrom')
  parser.add_argument('--lines', '-l', dest='lines', type=str,
                      help='Plot specified lines.')
  parser.add_argument('--title', '-t', dest='title', type=str, help='Plot title')
  parser.add_argument('--suptitle', '-s', dest='suptitle', type=str, help='Plot super-title, appears above title')
  parser.add_argument('--listlines', '-L', action='store_true',
      help='List available lines')
  parser.add_argument('--reference', '-r', dest='reference', type=str,
      help='Plot a reference spectra')

  args = parser.parse_args()

  if args.listlines:
    for k, v in element_lines.iteritems():
      print "%4s %s" % (k, v)
    exit()

  hdulist = pyfits.open(args.filename)
  print hdulist.info()

  image_spectra = ImageSpectra(hdulist[0].data)

  graph_subplot = plt.subplot(211)
  graph_subplot.set_ylabel('Relative intensity')

  image_subplot = plt.subplot(212)
  image_subplot.set_xlabel('x px')
  image_subplot.set_ylabel('y px')
  image_spectra.plot_image_onto(image_subplot)

  plots = []
  plots.append(image_spectra)

  if args.calibration:
    reference_1, reference_2 = args.calibration.split(',')
    pixel1, angstrom1 = reference_1.split(':')
    pixel2, angstrom2 = reference_2.split(':')

    if angstrom1 in element_lines:
      angstrom1 = element_lines[angstrom1].angstrom
    if angstrom2 in element_lines:
      angstrom2 = element_lines[angstrom2].angstrom

    calibration = Calibration(CalibrationReference(int(pixel1),float(angstrom1)),
                              CalibrationReference(int(pixel2), float(angstrom2)))

    print calibration

    image_spectra.set_calibration(calibration)

    if args.lines:
      lines_to_plot = args.lines.split(',')

      for line_to_plot in lines_to_plot:
        line = element_lines[line_to_plot]
        plots.append(line)

    graph_subplot.axvline(x=0, color='yellow')
    graph_subplot.set_xlabel(r'Wavelength ($\AA$)')

    if args.reference:
      reference = Reference(args.reference)
      reference.scale_to(image_spectra)
      plots.append(reference)

      graph_subplot.set_xlim(left=3900,right=7000)
      # FIXME
      graph_subplot.set_ylim(top=50000)

      plots.append(CorrectedSpectra(image_spectra, reference))

  else:
    graph_subplot.set_xlabel('Pixel')
    

  if args.title:
    title = args.title
  else:
    title = args.filename

  plt.title(title)

  if args.suptitle:
    plt.suptitle(args.suptitle)

  for plot in plots:
    plot.plot_onto(graph_subplot)

  graph_subplot.legend(loc='best')

  plt.show()

if __name__ == '__main__':
  main()