from typing import Self
from pylogic.base import _PylogicObject, to_dict
import json
import pytest


class MockPylogicObject(_PylogicObject):
    child_independent_attrs = _PylogicObject.child_independent_attrs + ("name",)
    child_dependent_attrs = _PylogicObject.child_dependent_attrs
    __slots__ = child_dependent_attrs + child_independent_attrs

    def __init__(self, name: str | None = None, children=None, **kwargs):
        super().__init__(children=children, name=name, **kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MockPylogicObject):
            return NotImplemented
        return self.name == other.name and self.children == other.children

    def __hash__(self) -> int:
        return hash((self.name, *self.children))

    def __repr__(self) -> str:
        return f"MockPylogicObject({self.name}, children={self.children})"

    def update_child_dependent_attrs(self) -> None:
        return super().update_child_dependent_attrs()

    def init_child_independent_attrs(self, name: str) -> None:
        self.name = name

    def update_child_independent_attrs(self, reference_object: Self) -> None:
        self.name = reference_object.name


def setup():
    obj1 = MockPylogicObject("1")
    obj2 = MockPylogicObject("2")
    obj3 = MockPylogicObject("3", children=[obj1, obj2])
    obj4 = MockPylogicObject("4", children=[obj3, obj2])
    obj5 = MockPylogicObject("5", children=[obj4, obj1, obj3])
    return obj1, obj2, obj3, obj4, obj5


def t_name():
    obj1, obj2, obj3, obj4, obj5 = setup()
    assert obj1.name == "1"
    assert obj2.name == "2"
    assert obj3.name == "3"
    assert obj4.name == "4"
    assert obj5.name == "5"


def t_children():
    obj1, obj2, obj3, obj4, obj5 = setup()
    assert obj1.children == []
    assert obj2.children == []
    assert obj3.children == [obj1, obj2]
    assert obj4.children == [obj3, obj2]
    assert obj5.children == [obj4, obj1, obj3]


def t_replace_all_positions_none():
    """
    Should replace all instances of obj1 with obj2 in obj5."""
    obj1, obj2, obj3, obj4, obj5 = setup()
    new_obj = obj5.replace({obj1: obj2})
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("2"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("2"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("2"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1, obj3]


def t_replace_all_positions_single_empty():
    """
    Should not replace anything.
    """
    obj1, obj2, obj3, obj4, obj5 = setup()
    new_obj = obj5.replace({obj1: obj2}, positions=[[]])
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("1"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1, obj3]


def t_replace_positions_empty():
    """
    Should not replace anything.
    """
    obj1, obj2, obj3, obj4, obj5 = setup()
    new_obj = obj5.replace({obj1: obj2}, positions=[])
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("1"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1, obj3]
    assert new_obj == obj5


def t_replace_specific_position():
    """
    Should replace obj1 with obj2 in the first child of obj5.
    """
    obj1, obj2, obj3, obj4, obj5 = setup()
    new_obj = obj5.replace({obj1: obj2}, positions=[[0]])
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("2"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("1"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1, obj3]


def t_replace_specific_multiple_positions():
    """
    Should replace obj1 with obj2 in the first child of the first child of obj5 and
    the third child of obj5.
    """
    obj1, obj2, obj3, obj4, obj5 = setup()
    new_obj = obj5.replace({obj1: obj2}, positions=[[0, 0], [2]])
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("2"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("1"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("2"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1, obj3]


def t_replace_positions_oob():
    """
    Should not replace anything because the specified position is out of bounds.
    """
    obj1, obj2, obj3, obj4, obj5 = setup()
    new_obj = obj5.replace({obj1: obj2}, positions=[[0, 4]])
    # child at index 0 does not have a child at index 4, so this
    # should not replace anything
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("1"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1, obj3]


def t_replace_user_invalid_internal_args():
    """
    Should raise an error when invalid internal arguments are passed.
    """
    obj1, obj2, obj3, obj4, obj5 = setup()
    with pytest.raises(
        ValueError,
        match="Depth must be at most the length of the path if path is provided.",
    ):
        obj5.replace({obj1: obj2}, _path=[], _depth=1)


def t_replace_with_different_equal_check():
    """
    Should replace obj1b with obj2 in obj5, but only if the objects are equal
    according to the provided equal_check function.
    """
    obj1, obj2, obj3, obj4, _ = setup()
    obj1b = MockPylogicObject("1")
    obj5 = MockPylogicObject("5", children=[obj4, obj1b, obj3])
    new_obj = obj5.replace({obj1b: obj2}, equal_check=lambda x, y: x is y)
    assert new_obj == MockPylogicObject(
        "5",
        children=[
            MockPylogicObject(
                "4",
                children=[
                    MockPylogicObject(
                        "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
                    ),
                    MockPylogicObject("2"),
                ],
            ),
            MockPylogicObject("2"),
            MockPylogicObject(
                "3", children=[MockPylogicObject("1"), MockPylogicObject("2")]
            ),
        ],
    )
    assert obj5.children == [obj4, obj1b, obj3]
