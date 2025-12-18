from typing import List

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok

from .layer import Section, Substrate, MultiLayer

Warning = str


class Profile(list[Section]):
    def validate(self) -> Result[List[Warning], List[Exception]]:
        warnings: List[Warning] = []
        errors: List[Exception] = []

        if len(self) == 0:
            errors.append(ValueError("Profile must contain at least one section."))

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
        flattened: List[Section] = []
        for section in self:
            if isinstance(section, MultiLayer):
                flattened.extend(section.layers * section.repeat)
            else:
                flattened.append(section)
        return flattened
