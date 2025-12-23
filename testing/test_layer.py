from returns.pipeline import is_successful as ok

from gsapdef import Material, Layer, MultiLayer
from gsapdef.layer import Medium


def test_Medium():
    assert ok(Medium(material=Material(code="Si")).validate())
    assert ok(Medium(material=("Si", 2.33)).validate())


def test_layer():
    assert ok(Layer(material=Material(code="Al"), thickness=10.0).validate())
    assert ok(Layer(material=("Al", 2.699), thickness=100.0).validate())
    assert not ok(Layer(material=Material(code="Al"), thickness=-5.0).validate())


def test_multilayer():
    assert ok(
        MultiLayer(
            layers=[
                Layer(material=Material(code="Al"), thickness=10.0),
                Layer(material=Material(code="Si"), thickness=5.0),
            ],
            repeat=5,
        ).validate()
    )

    assert not ok(
        MultiLayer(
            layers=[
                Layer(material=Material(code="Al"), thickness=10.0),
                Layer(material=Material(code="Si"), thickness=-5.0),
            ],
            repeat=5,
        ).validate()
    )

    assert not ok(
        MultiLayer(
            layers=[
                Layer(material=Material(code="Al"), thickness=10.0),
                Layer(material=Material(code="Si"), thickness=5.0),
            ],
            repeat=-5,
        ).validate()
    )

    invalid_instance = MultiLayer(
        layers=[
            Layer(material=Material(code="Al"), thickness=10.0),
            Layer(material=Material(code="Si"), thickness=-5.0),
        ],
        repeat=-5,
    )
    assert not ok(invalid_instance.validate())
    assert (
        len(invalid_instance.validate().failure()) == 2
    )  # One error from Layer thickness and one from MultiLayer repeat
