from returns.pipeline import is_successful as ok

from gsapdef import Material
from gsapdef.material import CompositionType


def test_material():
    # test weight fraction composition
    mat = Material(code="Al0.5N0.5")
    assert mat.composition_type() == CompositionType.WEIGHT_FRACTION
    assert ok(mat.validate())

    # test stoichiometric composition
    mat = Material(code="Al7N7Sc6")
    assert mat.composition_type() == CompositionType.STOICHIOMETRIC
    assert ok(mat.validate())

    assert ok(Material(code="(AlN)0.7(ScN)0.3").validate())
    assert ok(Material(code="AlNSc").validate())

    assert not ok(Material(code="Al0.6N0.6").validate())  # invalid weight fractions sum
    assert not ok(Material(code="AlNSc", density=-2.0).validate())  # invalid density
