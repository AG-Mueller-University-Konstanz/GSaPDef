from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok
from returns.maybe import Maybe, Nothing

from ..error import Error as Err, Warning as Warn
from ..models.layer import Medium, Layer, Substrate


@dataclass
class Profile:
    layers: list[Medium] = field(default_factory=list)

    def __repr__(self) -> str:
        return "\n".join(
            [
                "Profile:",
                *(f"  {i+1}: {layer}" for i, layer in enumerate(self.layers)),
            ]
        )

    def validate(self) -> Result[Maybe[Warn], Err]:
        ProfileErr = Err.TypeErr("Profile")
        if len(self.layers) == 0:
            return Failure(ProfileErr("Profile must contain at least one layer"))

        has_substrate = False
        for i, layer in enumerate(self.layers):
            res = layer.validate()
            if ok(res) and (warn := res.unwrap()) != Nothing:
                print(f"Profile-Layer {i+1}: {warn.unwrap()}")

            if not ok(res):
                return Failure(ProfileErr(f"on layer {i+1}").stack(res.failure()))

            if isinstance(layer, Substrate):
                has_substrate = True
                if i < len(self.layers) - 1:
                    return Failure(ProfileErr(f"Substrate must be the last (bottom) layer, is @ position {i+1}"))

        if not has_substrate:
            return Failure(ProfileErr("No substrate layer defined"))

        return Success(Nothing)

    def diff(self, other: Profile) -> Result[Dict[str, tuple[str, str]], Err]:
        """Compares two profiles and returns a dict of differing layers"""
        if len(self.layers) != len(other.layers):
            return Failure(
                Err.NewErr(
                    "Dimension",
                    f"Different Dimensions (self: {len(self.layers)}, other: {len(other.layers)})",
                )
            )

        diffs: Dict[str, tuple[str, str]] = {}
        for i, (l1, l2) in enumerate(zip(self.layers, other.layers)):
            if l1 != l2:
                diffs[f"Layer {i+1}"] = (str(l1), str(l2))

        return Success(diffs)

    def __eq__(self, value) -> bool:
        if not isinstance(value, Profile):
            return False
        if len(self.layers) != len(value.layers):
            return False
        return all(l1 == l2 for l1, l2 in zip(self.layers, value.layers))

    def __ne__(self, value) -> bool:
        return not self.__eq__(value)
