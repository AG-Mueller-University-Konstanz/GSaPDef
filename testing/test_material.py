from returns.pipeline import is_successful as ok

from samplmodls import Material
from samplmodls.material import CompositionType


def test_material():
    mat = Material(code="Al0.5N0.5")
    assert list(mat.composition.keys()) == ["Al", "N"]
    assert list(mat.composition.values()) == [0.5, 0.5]
    assert mat.composition_type() == CompositionType.WEIGHT_FRACTION
    assert ok(mat.validate())

    mat = Material(code="Al0.6N0.6")
    assert not ok(mat.validate())

    mat = Material(code="Al7N7Sc6")
    assert mat.composition_type() == CompositionType.STOICHIOMETRIC
    assert ok(mat.validate())

    mat = Material(code="Al1N4", rougthness=3.0, transission_thickness=2.0)
    assert not ok(mat.validate())

    mat = Material(code="AlN", rougthness=7.0)
    assert ok(mat.validate())
    assert mat.validate().unwrap() != []  # should have a warning about high roughness
