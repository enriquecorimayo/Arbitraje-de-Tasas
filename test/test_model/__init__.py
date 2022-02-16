import unittest
loader = unittest.TestLoader()
start_dir = 'C:/Users/54112/source/repos/Arbitraje-de-Tasas/test/test_model'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)