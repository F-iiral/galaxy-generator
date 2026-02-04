from dataclasses import dataclass

@dataclass
class Parameters:
    size: int
    arms: int
    stars: int
    type: str

@dataclass
class GalaxyType:
    tightness: int
    bar: int
    core_spread: int
    core_chance: int

@dataclass
class Fragmentation:
    hyperlanes: float
    small_hyperlanes: float
    nebula: float
    stars: float
    spirals: float

@dataclass
class Disk:
    amount_factor: float

@dataclass
class Spirals:
    amount_factor: float

@dataclass
class Dust:
    amount_factor: float

@dataclass
class Nebula:
    amount_factor: float
    band_spacing: float
    band_thickness: float

@dataclass
class Hyperlanes:
    step_size: float
    main_length_factor: float
    main_length_alpha: float
    main_length_beta: float
    hyperlane_max_length_factor: float
    main_drift: float
    break_chance_max: float
    break_chance_min: float
    cluster_chance: float
    cluster_size_factor: float
    cluster_size_alpha: float
    cluster_size_beta: float
    branch_chance: float
    branch_length_factor: float
    branch_length_alpha: float
    branch_length_beta: float
    branch_drift_mu: float
    branch_drift_sigma: float
    special_generation_distance: int

@dataclass
class Generation:
    disk: Disk
    spirals: Spirals
    dust: Dust
    nebula: Nebula
    hyperlanes: Hyperlanes
    fragmentation: Fragmentation

    def __post_init__(self):
        self.disk = Disk(**self.disk)                               #type: ignore
        self.spirals = Spirals(**self.spirals)                      #type: ignore
        self.dust = Dust(**self.dust)                               #type: ignore
        self.nebula = Nebula(**self.nebula)                         #type: ignore
        self.hyperlanes = Hyperlanes(**self.hyperlanes)             #type: ignore
        self.fragmentation = Fragmentation(**self.fragmentation)    #type: ignore

@dataclass
class Steps:
    stars: bool
    spirals: bool
    nebula: bool
    dust: bool
    hyperlanes: bool

@dataclass
class Export:
    png: bool
    zip: bool

@dataclass
class Settings:
    manual: bool
    parameters: Parameters
    galaxy_types: dict[str, GalaxyType]
    generation: Generation
    steps: Steps
    export: Export

    def __post_init__(self):
        self.parameters = Parameters(**self.parameters) #type: ignore
        self.generation = Generation(**self.generation) #type: ignore
        self.galaxy_types = {
            key: GalaxyType(**value) if isinstance(value, dict) else value
            for key, value in self.galaxy_types.items()
        }
        self.steps = Steps(**self.steps) #type: ignore
        self.export = Export(**self.export) #type: ignore