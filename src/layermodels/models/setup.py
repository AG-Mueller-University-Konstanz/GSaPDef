from dataclasses import dataclass, field
from copy import deepcopy
from hashlib import sha256
from struct import unpack
from typing import cast

from returns.result import Result, Success, Failure
from returns.pipeline import is_successful as ok

from ..error import Error as Err
from ..printing import indent_block
from ..external.sessa import Geometry
from ..external.ter_sl import Form, Mode as FormMode
from ..models.layer import Substrate
from ..models.profile import Profile


@dataclass
class Setup:
    interface_thickness: float = field(default=0.0)  # in Angstroms
    energy: float = field(default=6000.0)  # in eV
    profile: Profile = field(default_factory=Profile)
    geometry: Geometry = field(default_factory=Geometry)
    ter_template: Form = field(default_factory=Form)

    def __repr__(self) -> str:
        return "\n".join(
            [
                "Setup:",
                indent_block(
                    "\n".join(
                        [
                            f"Energy: {self.energy}eV",
                            f"{self.profile}",
                            f"{self.geometry}",
                            f"{self.ter_template}",
                        ]
                    ),
                    2,
                ),
            ]
        )

    def summary(self) -> str:
        return "\n".join(
            [
                f"Energy: {self.energy}eV",
                f"{self.profile}",
                f"{self.geometry}",
                f"Template: {str(self.ter_template.parse())}",
            ]
        )

    def validate(self) -> Result[None, Err]:
        SetupErr = Err.TypeErr("Setup")

        if not self.interface_thickness > 0.0:
            return Failure(SetupErr(f"interface_thickness must be positive, got {self.interface_thickness}."))

        if not 50 <= self.energy <= 20000:
            return Failure(SetupErr(f"energy must be between 50 and 20000, got {self.energy}. (Enforced by Sessa)"))

        if not 0.01 <= (wave := round((12.398419739640716 / (self.energy / 1e3)), 6)) <= 1000.0:
            return Failure(SetupErr(f"wavelength must be between 0.01 and 1000.0 Å, got {wave}. (Enforced by TER-SL)"))

        if not ok(geo_res := self.geometry.validate()):
            return Failure(SetupErr("Invalid geometry.").stack(geo_res.failure()))

        if not ok(prof_res := self.profile.validate()):
            return Failure(SetupErr("Invalid profile.").stack(prof_res.failure()))

        if not ok(temp_res := self.ter_template.validate()):
            return Failure(SetupErr("Template is invalid.").stack(temp_res.failure()))

        return Success(None)

    def fill(self) -> None:
        if self.ter_template.source.mode[0] == FormMode.Source.AUTO:
            self.ter_template.source.mode = (FormMode.Source.ENERGY, self.energy)
        if self.ter_template.substrate.mode[0] == FormMode.Substrate.AUTO:
            substrate = cast(Substrate, self.profile.layers[-1])
            if substrate.material.density > 0.0:
                self.ter_template.substrate.mode = (
                    FormMode.Substrate.CHEMICAL,
                    (substrate.material.code, substrate.material.density),
                )
            else:
                self.ter_template.substrate.mode = (FormMode.Substrate.CODE, substrate.material.code)
        self.ter_template.profile = deepcopy(self.profile)

    def hash(self) -> int:
        repr = self.__repr__()
        digest = sha256(repr.encode("utf-8")).digest()
        return int(unpack(">q", digest[:8])[0])
