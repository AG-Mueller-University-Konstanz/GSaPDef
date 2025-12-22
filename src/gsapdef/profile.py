from typing import List

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok

from .layer import Section, Substrate, MultiLayer

Warning = str
"""Alias of str for warning messages."""


class Profile(list[Section]):
    """
    Represents a sample profile composed of multiple sections.
    Is a subclass of `list[Section]`.

    Methods
    -------
    validate() -> Result[List[Warning], List[Exception]]:
        Validates the profile's sections, returning warnings or errors as appropriate.
    flatten() -> List[Section]:
        Flattens the profile by expanding any MultiLayer sections into their constituent layers.

    Examples
    --------
    >>> profile = Profile(
    >>>     [
    >>>         Layer(material=("Al", 2.699), thickness=10.0),
    >>>         MultiLayer(
    >>>             layers=[
    >>>                 Layer(material=("Ni", 8.908), thickness=2.0),
    >>>                 Layer(material=("Cu", 8.96), thickness=3.0),
    >>>             ],
    >>>             repeat=4,
    >>>         ),
    >>>         Substrate(material=("Si", 2.33)),
    >>>     ],
    >>> )
    """

    def validate(self) -> Result[List[Warning], List[Exception]]:
        """
        Validates the profile's sections.

        Conditions
        ----------
        - The profile must contain at least one Section and one Substrate.
        - The Sections must be valid (delegated to matching Section subclass).
        - The Substrate must be the last section in the profile.

        Returns
        -------
        Result[List[Warning], List[Exception]]:
            - Success: List of warning messages if validation passes.
            - Failure: List of exceptions if validation fails.
        """
        warnings: List[Warning] = []
        errors: List[Exception] = []

        if not len(self) >= 2:
            errors.append(ValueError("Profile must contain at least one layer/multilayer and one substrate."))

        has_substrate = False
        for i, section in enumerate(self):
            if ok(sec_check := section.validate()):
                warnings.extend(sec_check.unwrap())
            else:
                errors.append(ExceptionGroup(f"field section[{i}]", sec_check.failure()))
            if isinstance(section, Substrate):
                has_substrate = True
                if i != len(self) - 1:
                    errors.append(ValueError(f"Substrate must be the last section in the profile, found @ index {i}."))

        if not has_substrate:
            errors.append(ValueError("Profile must contain a substrate section."))

        if errors:
            return Failure(errors)
        return Success(warnings)

    def flatten(self) -> List[Section]:
        """
        Flattens the profile by expanding any MultiLayer sections into their constituent layers.

        Returns
        -------
        List[Section]:
            A flattened list of sections with MultiLayers expanded.
        """
        flattened: List[Section] = []
        for section in self:
            if isinstance(section, MultiLayer):
                flattened.extend(section.layers * section.repeat)
            else:
                flattened.append(section)
        return flattened
