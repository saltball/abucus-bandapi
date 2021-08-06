import pathlib
import unittest
from bandapi.io.abacus.potential import AbacusPotential


class TestPotential(unittest.TestCase):
    def test_abacus_SG15(self):
        assert pathlib.Path(AbacusPotential(pot_name="SG15")["C"]).exists()

    @unittest.skipIf(not __import__("ase"), "Don't have `ase`")
    def test_abacus_SG15_with_ase(self):
        pathlib.Path(AbacusPotential(pot_name="SG15")[6]).exists()

    @unittest.skipIf(__import__("ase"), "Have `ase`")
    def test_abacus_SG15_without_ase(self):
        with self.assertRaises(ImportError):
            pathlib.Path(AbacusPotential(pot_name="SG15")[6]).exists()

    def test_abacus_SG15_not_exist(self):
        with self.assertRaises(KeyError):
            pathlib.Path(AbacusPotential(pot_name="SG15")["X"]).exists()


if __name__ == '__main__':
    unittest.main()
