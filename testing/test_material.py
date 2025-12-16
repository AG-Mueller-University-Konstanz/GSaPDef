import LayerModels
from LayerModels import Material


def test_material():
    mat = Material(code="Al0.5N0.5", density=3.26)
    assert mat.composition.keys() == {"Al", "N"}
    assert mat.composition.values() == {0.5, 0.5}
    assert mat.validate() == True

    mat = Material(code="Al0.6N0.6", density=2.65)
    assert mat.validate() == False
