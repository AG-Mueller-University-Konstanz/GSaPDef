from dataclasses import dataclass, field
import re
from typing import Dict, List
from enum import Enum

from returns.result import Result, Success, Failure


Warning = str


class CompositionType(Enum):
    STOICHIOMETRIC = "stoichiometric"
    WEIGHT_FRACTION = "weight_fraction"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class Material:
    code: str  # unique identifier, formatted as singleWord e.g. "Al0.35N0.35Sc0.3" or "AlNSc" or "Al7N7Sc6"
    density: float = field(default=0.0)  # in g/cm^3
    composition: Dict[str, float] = field(init=False)  # element symbol to stoichiometric ratio or weight fraction
    rougthness: float = field(default=0.0)  # in nm
    transission_thickness: float = field(default=0.0)  # thickness of transition layer in nm
    susceptibility: float = field(default=0.0)  # dimensionless
    deb_waller_factor: float = field(default=1.0)  # dimensionless

    def __post_init__(self) -> None:
        pattern = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)?")
        matches = pattern.findall(self.code)
        self.composition = {str(el): float(num) if num else 1.0 for el, num in matches}

    def composition_type(self) -> CompositionType:
        comp_values = list(self.composition.values())
        if all(map(lambda x: 0.0 < x < 1.0, comp_values)):
            return CompositionType.WEIGHT_FRACTION
        elif all(map(lambda x: x % 1 == 0.0, comp_values)) and all(map(lambda x: int(x) >= 1, comp_values)):
            return CompositionType.STOICHIOMETRIC
        else:
            return CompositionType.UNKNOWN

    def validate(self) -> Result[List[Warning], List[Exception]]:
        warns: List[Warning] = []
        errors: List[Exception] = []
        if self.code == "":
            errors.append(ValueError("Material code cannot be empty."))
        # if self.rougthness > 0.0 and self.transission_thickness > 0.0:
        #     errors.append(ValueError("The material rougthness and transission_thickness mutually exclusive."))
        if self.rougthness > 5.0:
            warns.append(
                f"A high roughness, got {self.rougthness}, (> 5 Å) may lead to inaccurate results. Use `transission_thickness=2*roughness` instead."
            )

        comp_type = self.composition_type()
        comp_values = list(self.composition.values())
        if not comp_type in [CompositionType.WEIGHT_FRACTION, CompositionType.STOICHIOMETRIC]:
            errors.append(
                ValueError(
                    "Element fractions must be between 0 and 1 for weight fractions or integers >= 1 for stoichiometric ratios."
                )
            )
        if comp_type == CompositionType.WEIGHT_FRACTION and not sum(comp_values) == 1.0:
            errors.append(
                ValueError(
                    f"Element weight fractions must sum to 1.0 for a weight fraction composition, got {sum(comp_values)}."
                )
            )

        if errors:
            return Failure(errors)
        return Success(warns)
