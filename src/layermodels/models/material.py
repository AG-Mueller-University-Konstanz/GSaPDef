from __future__ import annotations
from dataclasses import dataclass
import re

from returns.pipeline import is_successful as ok
from returns.result import Result, Success, Failure

from ..error import Error as Err


@dataclass
class Material:
    name: str
    code: str
    composition: dict[str, float]

    @classmethod
    def from_str(cls, code: str) -> Material:
        pattern = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)?")
        matches = pattern.findall(code)

        comp: dict[str, float] = {str(el): float(num) if num else 1.0 for el, num in matches}
        return cls(
            name="Undefined",
            code=code,
            composition=comp,
        )

    def validate(self) -> Result[None, Err]:
        MatErr = Err.TypeErr("Material")
        CompErr = Err.TypeErr("Composition")
        # TODO: check with materials database
        if self.code == "":
            return Failure(MatErr("An empty material code ('') was provided."))
        if not self.composition:
            return Failure(
                MatErr("Composition could not be identified from code.").stack(CompErr(f"Code: '{self.code}' => empty"))
            )

        return Success(None)
