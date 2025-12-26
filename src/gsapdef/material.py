from dataclasses import dataclass, field
from typing import List
from enum import Enum

from .chem import Formula

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok


Warning = str
"""Alias of str for warning messages."""


class CompositionType(Enum):
    """
    Possible composition states/types for a material.
    Attributes:
        UNKNOWN (-1): Composition does not fit any recognized type.
        STOICHIOMETRIC (0): Element ratios are given as integers **>= 1**
        WEIGHT_FRACTION (1): Element ratios are given as fractions between **0.0** and **1.0**. Used to describe a mixture of compounds.
    """

    UNKNOWN = -1
    STOICHIOMETRIC = 0
    WEIGHT_FRACTION = 1


@dataclass(slots=True)
class Material:
    """
    Represents a material with a unique code, density, and elemental composition.

    Attributes
    ----------
    code: str
        Unique identifier for the material. Example formats include "Al0.35N0.35Sc0.3", "AlNSc", or "Al7N7Sc6".
    density: float, optional
        Density of the material in g/cm^3.
        Default is 0.0.
    composition: Dict[str, float]
        Dictionary mapping element symbols to their stoichiometric ratios or weight fractions.

    Methods
    -------
    __post_init__() -> None
        Initializes the composition dictionary from the code string using regex.
        Element values default to 1.0 if not specified.
    composition_type() -> CompositionType
        Determines the type of composition (stoichiometric or weight fraction) based on the values.
    validate() -> Result[List[Warning], List[Exception]]
        Validates the material's attributes and composition, returning warnings or errors as appropriate.

    Examples
    --------
    >>> mat = Material(code="Al0.35N0.35Sc0.3", density=3.5678)
    >>> mat = Material(code="AlNSc", density=3.5678)
    >>> mat = Material(code="Al7N7Sc6", density=3.5678)
    """

    code: str
    """Unique identifier for the material."""
    density: float = field(default=0.0)
    """Density of the material in g/cm^3."""
    composition: Result[Formula, Exception] = field(init=False)
    """Init generated dictionary mapping element symbols to their ratios/fractions."""

    def __post_init__(self) -> None:
        """
        Generate the `composition` dictionary from the `code` string after initialization.
        """
        self.composition = Formula.from_string(self.code)

    def composition_type(self) -> CompositionType:
        """
        Determine the type of composition based on the values and state of the `composition` attribute.

        Returns
        -------
        CompositionType
            The type of composition: STOICHIOMETRIC, WEIGHT_FRACTION, or UNKNOWN.
            - STOICHIOMETRIC: All values can be expressed as non-truncated integers >= 1.
            - WEIGHT_FRACTION: All values are between 0.0 and 1.0.
            - UNKNOWN: Values do not fit either category or composition is invalid.

        Notes
        -----
        Only checks the first level of the formula; nested groups are not evaluated for composition type.
        """
        if not ok(self.composition):
            return CompositionType.UNKNOWN
        else:
            formula = self.composition.unwrap()
            values = list(map(lambda c: c.count, formula))
            if all(map(lambda x: 0.0 < x < 1.0, values)):
                return CompositionType.WEIGHT_FRACTION
            elif all(map(lambda x: x % 1 == 0.0, values)) and all(
                map(lambda x: int(x) >= 1, values)
            ):
                return CompositionType.STOICHIOMETRIC
            else:
                return CompositionType.UNKNOWN

    def validate(self) -> Result[List[Warning], List[Exception]]:
        """
        Validate the material's attributes and composition.

        Conditions
        ----------
        material.code :
            Must not be empty.
        material.density :
            Must not be negative.
        material.composition :
            - Composition type must be recognized (not UNKNOWN).
            - If weight fraction, values must sum to 1.0.

        Returns
        -------
            Result[List[Warning], List[Exception]]:
            - Success: List of warnings if validation passes with minor issues.
            - Failure: List of exceptions if validation fails.
        """

        warns: List[Warning] = []
        errors: List[Exception] = []
        if self.code == "":
            errors.append(ValueError("Material code cannot be empty."))

        if self.density < 0.0:
            errors.append(ValueError("Material density cannot be negative."))

        if not ok(self.composition):
            errors.append(self.composition.failure())
        else:
            match self.composition_type():
                case CompositionType.UNKNOWN:
                    errors.append(
                        ValueError(
                            "Material composition could not be classified as either stoichiometric or weighted fractions. Check formatting so that all subscripts are either integers >= 1 (stoichiometric) or floats between 0.0 and 1.0 (weighted fractions)."
                        )
                    )
                case CompositionType.STOICHIOMETRIC:
                    pass  # No additional checks for stoichiometric
                case CompositionType.WEIGHT_FRACTION:
                    # TODO: This should be alright, but needs to handle nested groups
                    formula = self.composition.unwrap()
                    if len(formula) == 1 and not formula[0].count == 1.0:
                        errors.append(
                            ValueError(
                                "Weighted fraction subscript for a composition with only one element must have a value of 1.0."
                            )
                        )
                    else:
                        counts = list(map(lambda c: c.count, formula))
                        if not abs(sum(counts) - 1.0) < 1e-6:
                            errors.append(
                                ValueError(
                                    f"Element subscripts must sum to 1.0 for a weighted fraction composition, got {sum(counts)}."
                                )
                            )

        if errors:
            return Failure(errors)
        return Success(warns)
