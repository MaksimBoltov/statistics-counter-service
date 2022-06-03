import pytest

from app import schemas


@pytest.mark.parametrize(
    "cost",
    [0, 1, 2000, 1.001, 1.006, 1.005],
)
def test_round_cost_validation(cost) -> None:
    """Testing custom 'cost' field validations with round."""
    input_data = {"date": "2000-01-01", "cost": cost}
    val = schemas.Statistics(**input_data)
    assert val.cost == round(cost, 2)
