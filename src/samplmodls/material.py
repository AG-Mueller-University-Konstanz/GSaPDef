from dataclasses import dataclass, field
import re
from typing import Dict, List
from enum import Enum

from returns.result import Result, Success, Failure


Warning = str
"""Alias of str for warning messages."""


class CompositionType(Enum):
    """
    Possible composition states/types for a material.
    Attributes:
        UNKNOWN (-1): Composition does not fit any recognized type.
        STOICHIOMETRIC (0): Element ratios are given as integers **>= 1**
        WEIGHT_FRACTION (1): Element ratios are given as fractions between **0.0** and **1.0**
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
    composition: Dict[str, float] = field(init=False)
    """Init generated dictionary mapping element symbols to their ratios/fractions."""
    # rougthness: float = field(default=0.0)  # in nm
    # transission_thickness: float = field(default=0.0)  # thickness of transition layer in nm
    # susceptibility: float = field(default=0.0)  # dimensionless
    # deb_waller_factor: float = field(default=1.0)  # dimensionless

    def __post_init__(self) -> None:
        """
        Generate the `composition` dictionary from the `code` string after initialization.

        Elements without specified values default to 1.0.
        """
        pattern = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)?")
        matches = pattern.findall(self.code)
        self.composition = {str(el): float(num) if num else 1.0 for el, num in matches}

    def composition_type(self) -> CompositionType:
        """
        Determine the type of composition based on the values in the `composition` dictionary.
        """
        comp_values = list(self.composition.values())
        if all(map(lambda x: 0.0 < x < 1.0, comp_values)):
            return CompositionType.WEIGHT_FRACTION
        elif all(map(lambda x: x % 1 == 0.0, comp_values)) and all(map(lambda x: int(x) >= 1, comp_values)):
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

        # if self.rougthness > 0.0 and self.transission_thickness > 0.0:
        #     errors.append(ValueError("The material rougthness and transission_thickness mutually exclusive."))
        # if self.rougthness > 5.0:
        #     warns.append(
        #         f"A high roughness, got {self.rougthness}, (> 5 Å) may lead to inaccurate results. Use `transission_thickness=2*roughness` instead."
        #     )

        comp_type = self.composition_type()
        comp_values = list(self.composition.values())
        if comp_type == CompositionType.UNKNOWN:
            errors.append(
                ValueError(
                    "Element fractions must be between 0 and 1 for weight fractions or integers >= 1 for stoichiometric ratios."
                )
            )
        if comp_type == CompositionType.WEIGHT_FRACTION and not round(sum(comp_values), 6) == 1.0:
            errors.append(
                ValueError(
                    f"Element weight fractions must sum to 1.0 for a weight fraction composition, got {sum(comp_values)}."
                )
            )

        if errors:
            return Failure(errors)
        return Success(warns)
