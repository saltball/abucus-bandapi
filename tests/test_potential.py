import pathlib
import pytest
from bandapi.io.abacus.potential import AbacusPotential


def test_abacus_SG15():
    assert pathlib.Path(AbacusPotential(pot_name="SG15")["C"]).exists()


@pytest.mark.skipif(not __import__("ase"), "Don't have `ase`")
def test_abacus_SG15_with_ase():
    with pytest.raises(ImportError) as e:
        pathlib.Path(AbacusPotential(pot_name="SG15")[6]).exists()
    assert isinstance(ImportError,e.type)


@pytest.mark.skipif(__import__("ase"), "Have `ase`")
def test_abacus_SG15_with_ase():
    pathlib.Path(AbacusPotential(pot_name="SG15")[6]).exists()


def test_abacus_SG15_not_exist():
    with pytest.raises(KeyError):
        pathlib.Path(AbacusPotential(pot_name="SG15")["X"]).exists()
