from typing import List

from pydantic import field_validator
from pydantic.dataclasses import dataclass


@dataclass
class Material:
    name: str
    concentration: float

    @field_validator("name")
    def strip_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Material name cannot be empty")
        return v

    @field_validator("concentration")
    def positive_concentration(cls, v):
        if v < 0:
            raise ValueError("Concentration must be >= 0")
        return v


@dataclass
class Formulation:
    name: str
    materials: List[Material]

    @field_validator("name")
    def strip_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Formulation name cannot be empty")
        return v

    @field_validator("materials")
    def check_unique_materials(cls, v):
        names = [m.name.lower() for m in v]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate material names are not allowed")
        if len(v) == 0:
            raise ValueError("Formulation must have at least one material")
        return v
