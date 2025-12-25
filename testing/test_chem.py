from gsapdef.chem import Formula
from returns.pipeline import is_successful as ok


def test_formula():
    # a formula that can be parsed is valid
    assert ok(Formula.from_string("C6H12O6"))
    assert ok(Formula.from_string("Mg(OH)2"))
    assert ok(Formula.from_string("(AlN)7(ScN)3"))
    assert ok(Formula.from_string("Mg(OH(ClO3))2"))

    # a formula that cannot be parsed is invalid
    assert not ok(Formula.from_string("C6H12O6)"))
    assert not ok(Formula.from_string("Mg(OH2"))
    assert not ok(Formula.from_string("(AlN7(ScN)3"))
    assert not ok(Formula.from_string("Mg(OH(ClO3)2"))
    assert not ok(Formula.from_string("C6/H12/O6"))


def test_elements():
    fomulas = [
        # formula, expected element set
        ("C6H12O6", {"C", "H", "O"}),
        ("Mg(OH)2", {"Mg", "O", "H"}),
        ("(AlN)7(ScN)3", {"Al", "N", "Sc"}),
        ("Mg(OH(ClO3))2", {"Mg", "O", "H", "Cl"}),
    ]

    for f in fomulas:
        formula_str, expected_elements = f
        result = Formula.from_string(formula_str)
        assert ok(result)
        formula = result.unwrap()
        elements = set(formula.elements())
        assert elements == expected_elements


def test_subscripts():
    fomulas = [
        # formula, expected element subscripts
        ("C6H12O6", [6.0, 12.0, 6.0]),
        ("Mg(OH)2", [1.0, ([1.0, 1.0], 2.0)]),
        ("(AlN)7(ScN)3", [([1.0, 1.0], 7.0), ([1.0, 1.0], 3.0)]),
        ("Mg(OH(ClO3))2", [1.0, ([1.0, 1.0, ([1.0, 3.0], 1.0)], 2.0)]),
    ]

    for f in fomulas:
        formula_str, expected_subscripts = f
        result = Formula.from_string(formula_str)
        assert ok(result)
        formula = result.unwrap()
        subscripts = formula.counts()
        assert subscripts == expected_subscripts


def test_chemical():
    valid_formulas = [
        "H2O",
        "AlScN",
        "HfO2",
        "C6H12O6",
        "Al2(SO4)3",
        "(AlN)7(ScN)3",
        "Mg(OH(ClO3))2",
    ]
    invalid_formulas = [
        "H2O0.5",
        "Al0.7Sc0.3N",
        "HfO2.5",
        "Mg(O0.5H0.5(Cl0.25O0.75))2",
    ]

    for formula in valid_formulas:
        assert ok(f := Formula.from_string(formula))
        formula_obj = f.unwrap()
        assert formula_obj.is_chem_valid()

    for formula in invalid_formulas:
        assert ok(f := Formula.from_string(formula))
        formula_obj = f.unwrap()
        assert not formula_obj.is_chem_valid()
