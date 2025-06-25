import os
import unittest
from panel_mantenimiento_general import verificar_estructura_inicial

class BasicTest(unittest.TestCase):
    def test_estructura(self):
        verificar_estructura_inicial()
        self.assertTrue(os.path.exists('config'))
        self.assertTrue(os.path.exists('logs'))

if __name__ == '__main__':
    unittest.main()
