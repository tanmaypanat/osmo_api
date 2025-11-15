from pydantic.dataclasses import dataclass


@dataclass
class Material:
    name: str
    concentration: float


@dataclass
class Formula:
    name: str
    materials: list[Material]
