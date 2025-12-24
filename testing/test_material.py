from returns.pipeline import is_successful as ok

import gsapdef as gpsd
from gsapdef import Material
from gsapdef.material import CompositionType


def test_material_composition():
    assert gpsd.material.get_components("Al0.5N0.5") == {"Al": 0.5, "N": 0.5}
    assert gpsd.material.get_components("Al7N7Sc6") == {"Al": 7.0, "N": 7.0, "Sc": 6.0}
    assert gpsd.material.get_components("AlNSc") == {"AlNSc": 1.0}
    assert gpsd.material.get_components("Al/N/Sc") == {"Al": 1.0, "N": 1.0, "Sc": 1.0}
    assert gpsd.material.get_components("Al7/N7/Sc3") == {
        "Al": 7.0,
        "N": 7.0,
        "Sc": 3.0,
    }
    assert gpsd.material.get_components("AlN7Sc3") == {"AlN": 7.0, "Sc": 3.0}
    assert gpsd.material.get_components("") == {}


def test_material():
    # test weight fraction composition
    mat = Material(code="Al0.5N0.5")
    assert mat.composition_type() == CompositionType.WEIGHT_FRACTION
    assert ok(mat.validate())

    # test stoichiometric composition
    mat = Material(code="Al7N7Sc6")
    assert mat.composition_type() == CompositionType.STOICHIOMETRIC
    assert ok(mat.validate())

    assert not ok(Material(code="Al0.6N0.6").validate())  # invalid weight fractions sum
    assert not ok(Material(code="AlNSc", density=-2.0).validate())  # invalid density
