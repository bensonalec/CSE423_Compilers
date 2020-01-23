import sys
sys.path.append('../src')

import unittest, run

class HelloWorld(unittest.TestCase):
  def test_hello_world(self):
    self.assertEqual(run.hello_world(), 'hello world')

	
if __name__ == '__main__':
	unittest.main()
