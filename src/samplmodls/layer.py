from dataclasses import dataclass, field
from typing import List

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok

from .material import Material


Warning = str


class Section:
    def validate(self) -> Result[List[Warning], List[Exception]]:
        return Success([])


@dataclass(slots=True)
class Medium(Section):
    material: Material

    def validate(self) -> Result[List[Warning], List[Exception]]:
        warnings: List[Warning] = []
        errors: List[Exception] = []

        if ok(mat_check := self.material.validate()):
            warnings.extend(mat_check.unwrap())
        else:
            errors.append(ExceptionGroup("field material", mat_check.failure()))

        if errors:
            return Failure(errors)
        return Success(warnings)


class Substrate(Medium):
    pass


@dataclass(slots=True)
class Layer(Medium):
    thickness: float  # in nm

    def validate(self) -> Result[List[Warning], List[Exception]]:
        warnings: List[Warning] = []
        errors: List[Exception] = []

        if ok(med_check := super().validate()):
            warnings.extend(med_check.unwrap())
        else:
            errors.append(ExceptionGroup("field material", med_check.failure()))

        if not self.thickness > 0:
            errors.append(ValueError("Thickness must be positive"))

        if errors:
            return Failure(errors)
        return Success(warnings)


@dataclass(slots=True)
class MultiLayer(Section):
    layers: List[Layer]
    repeat: int = field(default=1)

    def validate(self) -> Result[List[Warning], List[Exception]]:
        warnings: List[Warning] = []
        errors: List[Exception] = []

        for i, layer in enumerate(self.layers):
            if ok(layer_check := layer.validate()):
                warnings.extend(layer_check.unwrap())
            else:
                errors.append(ExceptionGroup(f"field layers[{i}]", layer_check.failure()))

        if errors:
            return Failure(errors)
        return Success(warnings)
