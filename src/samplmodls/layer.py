from dataclasses import dataclass, field
from typing import List

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok

from .material import Material


Warning = str
"""Alias of str for warning messages."""


@dataclass(slots=True)
class Section:
    """Base class for different sections in a sample profile.

    Methods
    -------
    validate() -> Result[List[Warning], List[Exception]]:
        Abstract method to validate the section's attributes.
    """

    def validate(self) -> Result[List[Warning], List[Exception]]:
        raise NotImplementedError("Subclasses must implement the validate method.")


@dataclass(slots=True)
class Medium(Section):
    """Represents a medium with a specific material.

    Attributes
    ----------
    material: Material
        The material associated with this medium.

    Methods
    -------
    validate() -> Result[List[Warning], List[Exception]]:
        Validates the medium's material, returning warnings or errors as appropriate.

    Examples
    --------
    >>> med = Medium(material=Material(code="Si", density=2.33))
    >>> med = Medium(material=("Si", 2.33))
    """

    material: Material

    def __init__(self, material: Material | tuple[str, float]) -> None:
        match material:
            case Material():
                self.material = material
            case (code, density):
                self.material = Material(code=code, density=density)
            case _:
                raise TypeError("material must be a Material instance or a (code, density) tuple")

    def validate(self) -> Result[List[Warning], List[Exception]]:
        """
        Validates the medium's material.

        Conditions
        ----------
        - `material` must be valid (delegated to Material).

        Returns
        -------
        Result[List[Warning], List[Exception]]:
            - Success: List of warnings if validation passes with minor issues.
            - Failure: List of exceptions if validation fails.
        """
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
    """
    Represents a substrate in a sample profile.
    Is effectively equivalent to Medium.

    Examples
    --------
    >>> substrate = Substrate(material=Material(code="Si", density=2.33))
    >>> substrate = Substrate(material=("Si", 2.33))
    """

    pass


@dataclass(slots=True)
class Layer(Medium):
    """
    Represents a layer in a sample profile with a specific thickness.

    Attributes
    ----------
    thickness: float
        Thickness of the layer in nanometers (nm).

    Methods
    -------
    __init__(material: Material | tuple[str, float], thickness: float) -> None:
        Initialize a Layer instance.
    validate() -> Result[List[Warning], List[Exception]]:
        Validates the layer's material and thickness, returning warnings or errors as appropriate.

    Examples
    --------
    >>> layer = Layer(material=Material(code="Al", density=2.699), thickness=100.0)
    >>> layer = Layer(material=("Al", 2.699), thickness=100.0)
    """

    thickness: float
    """Thickness of the layer in nanometers (nm)."""

    def __init__(self, material: Material | tuple[str, float], thickness: float) -> None:
        """
        Initialize a Layer instance.

        Parameters
        ----------
        material: Material | tuple[str, float]
            The material of the layer, either as a Material instance or a (code, density) tuple.
        thickness: float
            Thickness of the layer in nanometers (nm).

        Returns
        -------
        None
        """
        super(Layer, self).__init__(material=material)
        self.thickness = thickness

    def validate(self) -> Result[List[Warning], List[Exception]]:
        """
        Validate the layer's material and thickness.

        Conditions
        ----------
        - `material` must be valid (delegated to Medium).
        - `thickness` must be positive.

        Returns
        -------
        Result[List[Warning], List[Exception]]:
            - Success: List of warnings if validation passes with minor issues.
            - Failure: List of exceptions if validation fails.
        """
        warnings: List[Warning] = []
        errors: List[Exception] = []

        if ok(med_check := super(Layer, self).validate()):
            warnings.extend(med_check.unwrap())
        else:
            errors.append(ExceptionGroup("field material", med_check.failure()))

        if not self.thickness > 0:
            errors.append(ValueError(f"Thickness must be positive, got {self.thickness}"))

        if errors:
            return Failure(errors)
        return Success(warnings)


@dataclass(slots=True)
class MultiLayer(Section):
    """
    Represents a multilayer section composed of multiple layers repeated a certain number of times.

    Attributes
    ----------
    layers: List[Layer]
        List of layers that make up the multilayer section.
    repeat: int
        Number of times the layer sequence is repeated. Default is 1.

    Methods
    -------
    validate() -> Result[List[Warning], List[Exception]]:
        Validates each layer in the multilayer and the repeat count, returning warnings or errors as appropriate.

    Examples
    --------
    >>> multi = MultiLayer(
    >>>     layers=[
    >>>         Layer(material=Material(code="Si", density=2.33), thickness=50.0),
    >>>         Layer(material=Material(code="SiO2", density=2.65), thickness=20.0)
    >>>     ],
    >>>     repeat=10,
    >>> )
    """

    layers: List[Layer]
    repeat: int = field(default=1)
    """Number of times the layer sequence is repeated. Default is 1."""

    def validate(self) -> Result[List[Warning], List[Exception]]:
        """
        Validates each layer in the multilayer and the repeat count.

        Conditions
        ----------
        - Each `layer` must be valid (delegated to Layer).
        - `repeat` must be at least 1.

        Returns
        -------
        Result[List[Warning], List[Exception]]:
            - Success: List of warnings if validation passes with minor issues.
            - Failure: List of exceptions if validation fails.
        """
        warnings: List[Warning] = []
        errors: List[Exception] = []

        for i, layer in enumerate(self.layers):
            if ok(layer_check := layer.validate()):
                warnings.extend(layer_check.unwrap())
            else:
                errors.append(ExceptionGroup(f"field layers[{i}]", layer_check.failure()))

        if not self.repeat >= 1:
            errors.append(ValueError(f"Repeat must be at least 1, got {self.repeat}"))

        if errors:
            return Failure(errors)
        return Success(warnings)
