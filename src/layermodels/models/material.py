from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import re

from returns.pipeline import is_successful as ok
from returns.result import Result, Success, Failure

from ..error import Error as Err
from .. import caching as cache


@dataclass
class Material:
    name: str
    code: str
    composition: dict[str, float]
    density: float  # in g/cm3

    @classmethod
    def new(cls, material: str | tuple[str, float]) -> Material:
        if isinstance(material, str):
            return cls.from_str(material)
        else:
            return cls.from_tuple(material)

    @classmethod
    def from_str(cls, code: str) -> Material:
        pattern = re.compile(r"([A-Z][a-z]?)(\d*\.?\d*)?")
        matches = pattern.findall(code)

        comp: dict[str, float] = {str(el): float(num) if num else 1.0 for el, num in matches}
        return cls(
            name="Undefined",
            code=code,
            composition=comp,
            density=0.0,
        )

    @classmethod
    def from_tuple(cls, data: tuple[str, float]) -> Material:
        """Create a Material from (code, density) tuple."""
        code, density = data
        instance = cls.from_str(code)
        instance.density = density
        return instance

    def validate(self) -> Result[None, Err]:
        MatErr = Err.TypeErr("Material")
        CompErr = Err.TypeErr("Composition")
        DBErr = Err.TypeErr("Database")

        if self.code == "":
            return Failure(MatErr("An empty material code ('') was provided."))
        if not cache.Materials.valid:
            print(cache.Materials.valid)
            return Failure(DBErr("Materials database is could not be checked."))
        elif self.code not in cache.Materials.store.keys():
            return Failure(
                DBErr(
                    f"Material code '{self.code}' not found in the materials database, check spelling or either add a density or define it via LayerArgs."
                )
            )
        if not self.composition:
            return Failure(
                MatErr("Composition could not be identified from code.").stack(CompErr(f"Code: '{self.code}' => empty"))
            )

        return Success(None)
