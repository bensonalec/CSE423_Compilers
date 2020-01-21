import unittest, sys

sys.path.append('../src')
print(sys.path)
import run



class MyFirstTests(unittest.TestCase):
  def test_hello(self):
    self.assertEqual(run.hello_world(), 'hello world')

if __name__ == '__main__':
  unittest.main()

