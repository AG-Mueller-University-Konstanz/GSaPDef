from __future__ import annotations
from dataclasses import dataclass, field, is_dataclass
from typing import Generic, Optional, Any, TypeVar, Generator, cast
from itertools import product
from copy import deepcopy

from returns.maybe import Maybe, Some, Nothing

from ..models.material import Material
from ..models.layer import LayerArgs, Medium, Layer, Substrate, MultiLayer
from ..models.profile import Profile
from ..models.setup import Setup
from ..external.sessa import Orientation, Aperture, Geometry
from ..external.ter_sl import Form


autocount = 0


@dataclass
class Auto:
    label: str

    def __init__(self, label: str):
        self.label = label
        global autocount
        autocount += 1


def replace(field: Any, mapping: dict[str, Any]) -> Any:
    if isinstance(field, Auto):
        return mapping[field.label]
    return maybe_to_optional(field) if isinstance(field, Maybe) else field


def maybe_to_optional(m: Maybe[Any]) -> Optional[Any]:
    if isinstance(m, Some):
        return m.unwrap()
    return None


T = TypeVar("T")


class Spec(Generic[T]):

    def map(self, mapping: dict[str, Any]) -> T:
        """Recursively map a Spec to its corresponding model, substituting Auto values and converting Maybe to Optional."""
        target_type = specmap[self.__class__]
        mapped = {}
        for k, v in self.__dict__.items():
            if isinstance(v, list):

                def map_item(item: Any) -> Any:
                    if isinstance(item, Spec):
                        return item.map(mapping)
                    else:
                        return replace(item, mapping)

                mapped[k] = [map_item(item) for item in v]
            elif isinstance(v, Spec):
                mapped[k] = v.map(mapping)
            elif is_dataclass(v) and not isinstance(v, Auto):
                mapped[k] = deepcopy(cast(Any, v))
            else:
                mapped[k] = replace(v, mapping)
        return cast(T, target_type(**mapped))


@dataclass
class MediumSpec(Spec[Medium]):
    material: Material | Auto
    args: Maybe[LayerArgs | Auto]

    def __init__(self, material: Material | Auto | str | tuple[str, float], args: Optional[LayerArgs | Auto] = None):
        self.material = material if isinstance(material, (Material, Auto)) else Material.new(material)
        self.args = Some(args) if isinstance(args, (LayerArgs, Auto)) else Nothing


@dataclass
class LayerSpec(MediumSpec):
    thickness: int | Auto

    def __init__(
        self,
        thickness: int | Auto,
        material: Material | Auto | str | tuple[str, float],
        args: Optional[LayerArgs | Auto] = None,
    ):
        super().__init__(material, args)
        self.thickness = thickness


class SubstrateSpec(MediumSpec):
    pass


@dataclass
class MultiLayerSpec:
    layers: list[LayerSpec]


@dataclass
class ProfileSpec(Spec[Profile]):
    layers: list[MediumSpec]

    def __init__(self, layers: list[MediumSpec]):
        self.layers = layers


@dataclass
class OrientationSpec(Spec[Orientation]):
    phi: float | Auto = field(default=0.0)
    theta: float | Auto = field(default=0.0)


@dataclass
class ApertureSpec(Spec[Aperture]):
    phi_lower: float | Auto = field(default=0.0)
    phi_upper: float | Auto = field(default=0.0)
    theta_lower: float | Auto = field(default=0.0)
    theta_upper: float | Auto = field(default=0.0)


@dataclass
class GeometrySpec(Spec[Geometry]):
    aperture: ApertureSpec = field(default_factory=ApertureSpec)
    orientation_sample: OrientationSpec = field(default_factory=OrientationSpec)
    orientation_analyzer: OrientationSpec = field(default_factory=OrientationSpec)
    orientation_source: OrientationSpec = field(default_factory=OrientationSpec)
    polarization: OrientationSpec = field(default_factory=OrientationSpec)


@dataclass
class SetupSpec(Spec[Setup]):
    interface_thickness: float | Auto  # in Angstroms
    energy: float | Auto  # in eV
    profile: ProfileSpec
    geometry: GeometrySpec = field(default_factory=GeometrySpec)
    ter_template: Form = field(default_factory=Form)

    def __init__(
        self,
        interface_thickness: float | Auto,
        energy: float | Auto,
        profile: ProfileSpec,
        geometry: GeometrySpec = GeometrySpec(),
        ter_template: Form = Form(),
    ):
        self.interface_thickness = interface_thickness
        self.energy = energy
        self.profile = profile
        self.geometry = geometry
        self.ter_template = ter_template


specmap: dict[type, type] = {
    Form: Form,
    Material: Material,
    Profile: Profile,
    LayerArgs: LayerArgs,
    MediumSpec: Medium,
    SubstrateSpec: Substrate,
    LayerSpec: Layer,
    MultiLayerSpec: MultiLayer,
    ProfileSpec: Profile,
    OrientationSpec: Orientation,
    ApertureSpec: Aperture,
    GeometrySpec: Geometry,
    SetupSpec: Setup,
}


def expand(spec: SetupSpec, values: dict[str, list]) -> Generator[Setup, Any, Any]:
    global autocount
    assert (
        autocount == len(list(values.keys())) or autocount == 0
    ), 'Number of declared Variations ( "Auto(label)" ) does not match number of Variation provided to values.'

    if autocount == 0 and len(list(values.keys())) != 0:
        print("Warning:: The declared variations are currently not applied, missing Auto tags.")
        yield spec.map({})
        return
    # List of tag names in deterministic order
    tags = list(values.keys())
    # Iterate over all combinations
    for combo in product(*(values[tag] for tag in tags)):
        assignment = dict(zip(tags, combo))
        yield spec.map(assignment)
