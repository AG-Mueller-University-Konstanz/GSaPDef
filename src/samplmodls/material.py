from dataclasses import dataclass, field
from typing import Dict
import re


@dataclass(slots=True)
class Material:
    code: str  # unique identifier, formatted as singleWord e.g. "Al0.35N0.35Sc0.3" or "AlNSc"
    density: float  # in g/cm^3
    composition: dict[str, float] = field(init=False)  # element symbol to fraction by weight
    rougthness: float = field(default=0.0)  # in nm
    transission_thickness: float = field(default=0.0)  # thickness of transition layer in nm
    susceptibility: float = field(default=0.0)  # dimensionless
    deb_waller_factor: float = field(default=1.0)  # dimensionless

    def __init__(self, code: str, density: float = 0.0) -> None:
        super().__init__()
        self.code = code
        self.density = density

        pattern = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)?")
        matches = pattern.findall(code)
        self.composition: Dict[str, float] = {str(el): float(num) if num else 1.0 for el, num in matches}

    def validate(self) -> bool:
        return all(
            self.code != "",
            sum(self.composition.values()) == 1.0,
        )
