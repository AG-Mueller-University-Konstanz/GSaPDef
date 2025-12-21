from returns.pipeline import is_successful as ok

from samplmodls import Material, Substrate, Layer, MultiLayer, Profile


def test_profile():
    valid_instance = Profile(
        [
            Layer(material=Material(code="Al"), thickness=10.0),
            Layer(material=Material(code="Ti"), thickness=5.0),
            MultiLayer(
                layers=[
                    Layer(material=Material(code="Ni"), thickness=2.0),
                    Layer(material=Material(code="Cu"), thickness=3.0),
                ],
                repeat=4,
            ),
            Substrate(material=Material(code="Si")),
        ]
    )
    assert ok(valid_instance.validate())
    assert len(valid_instance.flatten()) == 2 + 4 * 2 + 1  # 2 Layers + 4*2 MultiLayer + 1 Substrate

    invalid_instance = Profile([])
    assert not ok(invalid_instance.validate())

    invalid_instance = Profile(
        [
            Layer(material=Material(code="Al"), thickness=10.0),
            Substrate(material=Material(code="Si")),
            Layer(material=Material(code="Ti"), thickness=5.0),  # Layer after Substrate
        ]
    )
    assert not ok(invalid_instance.validate())

    invalid_instance = Profile(
        [
            Layer(material=Material(code="Al"), thickness=10.0),
            Layer(material=Material(code="Ti"), thickness=5.0),
            # Missing Substrate
        ]
    )
    assert not ok(invalid_instance.validate())
