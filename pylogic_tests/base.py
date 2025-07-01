from typing import Self
from pylogic.base import _PylogicObject, to_dict
import json
import pytest
from unittest.mock import patch
import copy


class FakePylogicObject(_PylogicObject):
    child_independent_attrs = _PylogicObject.child_independent_attrs + ("name",)
    child_dependent_attrs = _PylogicObject.child_dependent_attrs
    __slots__ = child_dependent_attrs + child_independent_attrs

    def __init__(
        self,
        name: str | None = None,
        children: list[_PylogicObject] | None = None,
        **kwargs,
    ):
        super().__init__(children=children, name=name, **kwargs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FakePylogicObject):
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
    obj1 = FakePylogicObject("1")
    obj2 = FakePylogicObject("2")
    obj3 = FakePylogicObject("3", children=[obj1, obj2])
    obj4 = FakePylogicObject("4", children=[obj3, obj2])
    obj5 = FakePylogicObject("5", children=[obj4, obj1, obj3])
    return obj1, obj2, obj3, obj4, obj5


class TestInitialization:
    @patch("pylogic_tests.base.FakePylogicObject.update_child_dependent_attrs")
    def t_update_child_dependent_attrs(self, mock_update_child_dependent_attrs):
        """
        Should call the update_child_dependent_attrs method.
        """
        FakePylogicObject("1")
        mock_update_child_dependent_attrs.assert_called_once()

    @patch("pylogic_tests.base.FakePylogicObject.init_child_independent_attrs")
    def t_init_child_independent_attrs(self, mock_init_child_independent_attrs):
        """
        Should call the init_child_independent_attrs method.
        """
        FakePylogicObject("1")
        mock_init_child_independent_attrs.assert_called_once_with(name="1")

    @patch("pylogic_tests.base.FakePylogicObject.update_child_independent_attrs")
    def t_update_child_independent_attrs_copy(
        self, mock_update_child_independent_attrs
    ):
        """
        Should call the update_child_independent_attrs method.
        """
        obj1 = FakePylogicObject("1")
        copy.copy(obj1)
        mock_update_child_independent_attrs.assert_called_once_with(obj1)

    @patch("pylogic_tests.base.FakePylogicObject.update_child_independent_attrs")
    def t_update_child_independent_attrs_deepcopy(
        self, mock_update_child_independent_attrs
    ):
        """
        Should call the update_child_independent_attrs method.
        """
        obj1 = FakePylogicObject("1")
        copy.deepcopy(obj1)
        mock_update_child_independent_attrs.assert_called_once_with(obj1)

    def t_name(self):
        obj1, obj2, obj3, obj4, obj5 = setup()
        assert obj1.name == "1"
        assert obj2.name == "2"
        assert obj3.name == "3"
        assert obj4.name == "4"
        assert obj5.name == "5"

    def t_children(self):
        obj1, obj2, obj3, obj4, obj5 = setup()
        assert obj1.children == []
        assert obj2.children == []
        assert obj3.children == [obj1, obj2]
        assert obj4.children == [obj3, obj2]
        assert obj5.children == [obj4, obj1, obj3]


def t_hash():
    """
    Should preserve the hash of the object.
    """
    _, _, _, _, obj5 = setup()
    _, _, _, _, obj5_copy = setup()
    assert hash(obj5) == hash(obj5_copy)


class TestCopyAndDeepcopy:
    def t_copy(self):
        """
        Should create a shallow copy of the object.
        """
        _, _, _, _, obj5 = setup()
        obj5_copy = copy.copy(obj5)
        assert obj5_copy is not obj5
        assert obj5_copy.children is obj5.children
        assert obj5_copy == obj5

    def t_deepcopy(self):
        """
        Should create a deep copy of the object.
        """
        _, _, _, _, obj5 = setup()
        obj5_copy = copy.deepcopy(obj5)
        assert obj5_copy is not obj5
        assert obj5_copy.children is not obj5.children
        assert obj5_copy == obj5


class TestReplace:
    def t_replace_all_positions_none(self):
        """
        Should replace all instances of obj1 with obj2 in obj5.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2})
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("2"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("2"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("2"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_all_positions_single_empty(self):
        """
        Should not replace anything.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2}, positions=[[]])
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("1"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("1"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("1"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_positions_empty(self):
        """
        Should not replace anything.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2}, positions=[])
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("1"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("1"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("1"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]
        assert new_obj == obj5

    def t_replace_specific_position(self):
        """
        Should replace obj1 with obj2 in the first child of obj5.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2}, positions=[[0]])
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("2"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("1"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("1"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_specific_multiple_positions(self):
        """
        Should replace obj1 with obj2 in the first child of the first child of obj5 and
        the third child of obj5.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2}, positions=[[0, 0], [2]])
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("2"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("1"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("2"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_specific_position_self_reference(self):
        """
        Should replace obj1 with obj5 at the specific position.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj5}, positions=[[0]])
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject("3", children=[obj5, FakePylogicObject("2")]),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("1"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("1"), FakePylogicObject("2")]
                ),
            ],
        )
        assert new_obj.children[0].children[0].children[0] is obj5
        assert new_obj.children[0].children[0].children[0] is not new_obj
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_positions_oob(self):
        """
        Should not replace anything because the specified position is out of bounds.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2}, positions=[[0, 4]])
        # child at index 0 does not have a child at index 4, so this
        # should not replace anything
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("1"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("1"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("1"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_user_invalid_internal_args(self):
        """
        Should raise an error when invalid internal arguments are passed.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        with pytest.raises(
            ValueError,
            match="Depth must be at most the length of the path if path is provided.",
        ):
            obj5.replace({obj1: obj2}, _path=[], _depth=1)

    def t_replace_self(self):
        """
        Should replace obj1 with itself in obj5, effectively making no change.
        """
        obj1, _, _, _, obj5 = setup()
        new_obj = obj5.replace({obj1: obj1})
        assert new_obj == obj5

    def t_replace_self_with_copy(self):
        """
        Should replace obj1 with a copy of itself in obj5, effectively making no change.
        """
        obj1, _, _, _, obj5 = setup()
        new_obj = obj5.replace({obj1: copy.copy(obj1)})
        assert new_obj == obj5

    def t_replace_self_with_deepcopy(self):
        """
        Should replace obj1 with a deep copy of itself in obj5, effectively making no
        change.
        """
        obj1, _, _, _, obj5 = setup()
        new_obj = obj5.replace({obj1: copy.deepcopy(obj1)})
        assert new_obj == obj5

    def t_replace_self_self(self):
        """
        Should replace obj5 with itself in obj5, effectively making no change.
        """
        _, _, _, _, obj5 = setup()
        new_obj = obj5.replace({obj5: obj5})
        assert new_obj == obj5
        assert new_obj is obj5

    def t_replace_idempotent_when_key_is_not_child(self):
        """
        When a key in `replace_dict` is not a descendant of its value,
        `replace` should be idempotent.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2})
        assert new_obj == new_obj.replace({obj1: obj2})

    def t_replace_not_idempotent_when_key_is_child(self):
        """
        When a key in `replace_dict` is a descendant of its value,
        `replace` should not be idempotent.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj5})
        assert new_obj != new_obj.replace({obj1: obj5})

    def t_replace_with_different_equal_check(self):
        """
        Should replace obj1b with obj2 in obj5, but only if the objects are equal
        according to the provided equal_check function.
        """
        obj1, obj2, obj3, obj4, _ = setup()
        obj1b = FakePylogicObject("1")
        obj5 = FakePylogicObject("5", children=[obj4, obj1b, obj3])
        new_obj = obj5.replace({obj1b: obj2}, equal_check=lambda x, y: x is y)
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("1"), FakePylogicObject("2")],
                        ),
                        FakePylogicObject("2"),
                    ],
                ),
                FakePylogicObject("2"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("1"), FakePylogicObject("2")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1b, obj3]
