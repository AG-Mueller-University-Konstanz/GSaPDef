from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable, Optional

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok
from returns.maybe import Maybe, Some, Nothing

from ..error import Error as Err, Warning as Warn
from ..models.material import Material


@dataclass
class LayerArgs:
    code1: Maybe[str] = Nothing  # chemical formula
    code2: Maybe[str] = Nothing  # chemical formula
    code3: Maybe[str] = Nothing  # chemical formula
    code4: Maybe[str] = Nothing  # chemical formula
    x1: Maybe[float] = Nothing  # composition fraction of code1
    x2: Maybe[float] = Nothing  # composition fraction of code2
    x3: Maybe[float] = Nothing  # composition fraction of code3
    sigma: Maybe[float] = Nothing  # rms roughness in Å
    tr: Maybe[float] = Nothing  # transition layer thickness in Å
    chi0: Maybe[float] = Nothing  # layer x-ray susceptibility
    deb_wall: Maybe[float] = Nothing  # Debye-Waller factor

    def __init__(
        self,
        codes: Optional[tuple[str, ...]] = None,
        composition: Optional[tuple[float, ...]] = None,
        sigma: Optional[float] = None,
        tr: Optional[float] = None,
        chi0: Optional[float] = None,
        deb_wall: Optional[float] = None,
    ):
        if codes is not None:
            self.code1, self.code2, self.code3, self.code4 = (
                Some(codes[0]) if len(codes) > 0 else Nothing,
                Some(codes[1]) if len(codes) > 1 else Nothing,
                Some(codes[2]) if len(codes) > 2 else Nothing,
                Some(codes[3]) if len(codes) > 3 else Nothing,
            )
        if composition is not None:
            self.x1, self.x2, self.x3 = (
                Some(composition[0]) if len(composition) > 0 else Nothing,
                Some(composition[1]) if len(composition) > 1 else Nothing,
                Some(composition[2]) if len(composition) > 2 else Nothing,
            )
        self.sigma = Some(sigma) if sigma is not None else Nothing
        self.tr = Some(tr) if tr is not None else Nothing
        self.chi0 = Some(chi0) if chi0 is not None else Nothing
        self.deb_wall = Some(deb_wall) if deb_wall is not None else Nothing

    def __repr__(self) -> str:
        if self == LayerArgs():
            return "LayerArgs(default)"
        else:
            return f"LayerArgs({', '.join(f'{k}={v}' for k, v in self.__dict__.items() if v != Nothing)})"

    def validate(self) -> Result[Maybe[str], Err]:
        ArgsErr = Err.TypeErr("LayerArgs")
        if self.sigma != Nothing and self.tr != Nothing:
            return Failure(ArgsErr("Both tr and sigma are defined (mutually exclusive)"))
        if self.sigma != Nothing and self.sigma.unwrap() > 5:
            return Success(
                Some("Warning: High roughness (sigma > 5 Å) may lead to inaccurate results. Use tr=2*(sigma) instead.")
            )

        num_codes = len([c for c in [self.code1, self.code2, self.code3, self.code4] if c != Nothing])
        num_comps = len([x for x in [self.x1, self.x2, self.x3] if x != Nothing])
        if num_codes != num_comps or num_codes > 1 + num_comps:
            return Failure(
                ArgsErr(
                    "The number of defined codes and compositional fractions do not match. Check that for N defined codes, at most N-1 composition fractions are defined.",
                )
            )

        if sum(x.unwrap() for x in [self.x1, self.x2, self.x3] if x != Nothing) > 1.0:
            return Failure(ArgsErr("Sum of composition fractions exceeds 1.0"))

        if (
            all(x != Nothing for x in [self.code1, self.code2, self.code3, self.code4])  # check all codes defined
            and all(x != Nothing for x in [self.x1, self.x2, self.x3])  # check first three fractions defined
            and sum(x.unwrap() for x in [self.x1, self.x2, self.x3]) == 1.0  # check sum of first three fractions
        ):
            return Failure(
                ArgsErr(
                    "Sum of composition fractions is exactly 1.0 but code4 is defined => implicit fraction of 0 for code4",
                )
            )

        return Success(Nothing)


@dataclass
class Medium:
    material: Material
    args: Maybe[LayerArgs]

    def __init__(self, material: Material | str | tuple[str, float], args: Optional[LayerArgs] = None):
        self.material = material if isinstance(material, Material) else Material.new(material)
        self.args = Some(args) if isinstance(args, LayerArgs) else Nothing

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(material={self.material}, args={self.args})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Medium):
            return False
        return self.material == other.material and self.args == other.args

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def validate(self) -> Result[Maybe[Warn], Err]:
        MedErr = Err.TypeErr("Medium")
        if not ok(mat_res := self.material.validate()):
            return Failure(MedErr("field material").stack(mat_res.failure()))

        if self.args != Nothing:
            if not ok(arg_res := self.args.unwrap().validate()):
                return Failure(MedErr("field args").stack(arg_res.failure()))
            if ok(arg_res) and (warn := arg_res.unwrap()) != Nothing:
                return Success(Some(warn.unwrap()))
        return Success(Nothing)


class Substrate(Medium):
    pass


@dataclass
class Layer(Medium):
    thickness: int  # in Å

    def __init__(self, thickness: int, material: Material | str | tuple[str, float], args: Optional[LayerArgs] = None):
        self.thickness = thickness
        super().__init__(material, args)

    def __repr__(self) -> str:
        return f"Layer(thickness={self.thickness}, material={self.material}, args={self.args})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Layer):
            return False
        return self.thickness == other.thickness and self.material == other.material and self.args == other.args

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def validate(self) -> Result[Maybe[Warn], Err]:
        LayerErr = Err.TypeErr("Layer")
        if not self.thickness > 0:
            return Failure(LayerErr("Thickness must be > 0"))
        return super().validate()


@dataclass
class MultiLayer:
    layers: list[Layer] = field(default_factory=list)

    def __init__(self, layers: Iterable[Layer]):
        self.layers = list(layers)
