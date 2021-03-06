import unittest
import specreduce

class CalibrationReferenceTests(unittest.TestCase):

  def setUp(self):
    self.cr = specreduce.CalibrationReference(42, 99)

  def testPixel(self):
    self.assertEqual(self.cr.pixel, 42)

  def testAngstrom(self):
    self.assertEqual(self.cr.angstrom, 99)


def main():
  unittest.main()

if __name__ == '__main__':
  main()
