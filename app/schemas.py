from pydantic.dataclasses import dataclass


@dataclass
class Material:
    name: str
    concentration: float


@dataclass
class Formulation:
    name: str
    materials: list[Material]
