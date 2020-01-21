import unittest
from ../src/run import *
class MyFirstTests(unittest.TestCase):
  def test_hello(self):
    self.assertEqual(hello_world(), 'yello world')

if __name__ == '__main__':
  unittest.main()
