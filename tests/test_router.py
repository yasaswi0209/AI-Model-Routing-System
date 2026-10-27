import unittest
from router import route
from core import pricing
from unittest.mock import patch
class RouterTests(unittest.TestCase):
 def test_short(self): self.assertEqual(route('What is Python?')[0],'small')
 def test_code(self): self.assertEqual(route('```python\nx=1\n```')[0],'large')
 def test_complex(self): self.assertEqual(route('Compare SQL and NoSQL')[0],'large')
 def test_no_configured_cost(self):
  with patch.dict('os.environ',{},clear=True): self.assertIsNone(pricing('small',100,50))
 def test_configured_cost(self):
  with patch.dict('os.environ',{'SMALL_INPUT_USD_PER_MILLION':'1','SMALL_OUTPUT_USD_PER_MILLION':'2'}): self.assertAlmostEqual(pricing('small',100,50),.0002)
if __name__=='__main__': unittest.main()
