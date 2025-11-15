import pytest
from pydantic import ValidationError
from app.schemas import Material, Formulation


def test_material_creation():
    mat = Material(name="Lavender Oil", concentration=10.5)
    assert mat.name == "Lavender Oil"
    assert mat.concentration == 10.5


def test_material_invalid_concentration():
    with pytest.raises(ValidationError):
        # concentration should be float, passing string triggers validation
        Material(name="Lavender Oil", concentration="high")


def test_formulation_creation():
    materials = [
        Material(name="Bergamot Oil", concentration=15.5),
        Material(name="Lavender Oil", concentration=10.0),
    ]
    formulation = Formulation(name="Summer Breeze", materials=materials)

    assert formulation.name == "Summer Breeze"
    assert len(formulation.materials) == 2
    assert formulation.materials[0].name == "Bergamot Oil"


def test_formulation_invalid_materials():
    # materials should be list of Material
    with pytest.raises(ValidationError):
        Formulation(name="Test", materials=["not a material"])
