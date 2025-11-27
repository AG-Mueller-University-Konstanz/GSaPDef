from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

import numpy as np
from numpy.typing import NDArray

from .. import caching as Cache
from ..models.setup import Setup
from ..external.sessa import Peak
from ..external.ter_sl import Grid


@dataclass
class Simulation:
    id: int
    setup: Setup
    peaks: list[Peak] = field(default_factory=list)
    peaks_grouped: Dict[str, list[Peak]] = field(default_factory=dict)
    imfps: list[NDArray[np.float64]] = field(default_factory=list)  # inelastic mean free paths
    #
    peaks_filtered: NDArray[np.bool] = field(default_factory=lambda: np.array([]))
    peaks_grouped_filtered: Dict[str, NDArray[np.bool]] = field(default_factory=dict)
    grid: Grid = field(default_factory=Grid)
    damping_tensor: NDArray[np.float64] = field(default_factory=lambda: np.array([]))  # (angle, depth, peak)
    damping_map: Dict[str, Dict[str, NDArray[np.float64]]] = field(
        default_factory=dict
    )  # element (Peak) -> damping 2D array (angle, depth)
    damped_tensor: NDArray[np.float64] = field(default_factory=lambda: np.array([]))  # (angle, depth, peak)
    rocking_matrix: NDArray[np.float64] = field(default_factory=lambda: np.array([]))  # (angle, peak)
    sensitivity_tensor: NDArray[np.int32] = field(
        default_factory=lambda: np.array([])
    )  # (angle, (layer, intervals), peak)

    def __init__(self, id: int, setup: Setup):
        self.id = id
        self.setup = setup
        self.peaks = []
        self.peaks_grouped = {}
        self.imfps = []
        self.peaks_filtered = np.array([])
        self.peaks_grouped_filtered = {}
        self.grid = Grid()
        self.damping = np.array([])
        self.damping_map = {}
        self.results = np.array([])

    @classmethod
    def from_list(cls, setups: list[Setup]) -> list[Simulation]:
        start_id = Cache.State.start_run
        return [cls(id=start_id + i, setup=setup) for i, setup in enumerate(setups)]
