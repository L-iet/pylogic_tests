from typing import Self
from pylogic.base import _PylogicObject
import json
import pytest
from unittest.mock import patch
import copy


class FakePylogicObject(_PylogicObject):
    child_independent_attrs = _PylogicObject.child_independent_attrs + ("name",)
    child_dependent_attrs = _PylogicObject.child_dependent_attrs
    hash_attrs = _PylogicObject.hash_attrs + ("name",)
    __slots__ = child_dependent_attrs + child_independent_attrs

    def __init__(
        self,
        name: str | None = None,
        children: list[_PylogicObject] | None = None,
        **kwargs,
    ):
        super().__init__(children=children, name=name, **kwargs)

    def update_child_dependent_attrs(self) -> None:
        return super().update_child_dependent_attrs()

    def init_child_independent_attrs(self, name: str) -> None:
        self.name = name

    def update_child_independent_attrs(self, reference_object: Self) -> None:
        self.name = reference_object.name


class FakeSubclass(FakePylogicObject): ...


class FakeSubclass2(FakePylogicObject):
    child_independent_attrs = FakePylogicObject.child_independent_attrs + (
        "extra_attr",
    )
    __slots__ = FakePylogicObject.child_dependent_attrs + child_independent_attrs


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

    def t_leaves(self):
        obj1, obj2, obj3, obj4, obj5 = setup()
        assert obj1.leaves == []
        assert obj2.leaves == []
        assert obj3.leaves == [obj1, obj2]
        assert obj4.leaves == [obj1, obj2, obj2]
        assert obj5.leaves == [obj1, obj2, obj2, obj1, obj1, obj2]


class TestEquality:
    def t_equal(self):
        """
        Should be equal to another object with the same structure
        """
        _, _, _, _, obj5 = setup()
        _, _, _, _, obj5_copy = setup()
        assert obj5 == obj5_copy

    def t_not_equal_different_name(self):
        """
        Should not be equal to another object with a different name.
        """
        _, _, _, _, obj5 = setup()
        obj6 = FakePylogicObject("6", children=obj5.children)
        assert obj5 != obj6

    def t_not_equal_different_class(self):
        """
        Should not be equal to another object from a different class.
        """
        _, _, _, _, obj5 = setup()
        obj5subclass = FakeSubclass("5", children=obj5.children)
        assert obj5 != obj5subclass

    def t_equal_up_to_subclass(self):
        """
        Should be equal to another object with the same structure, ignoring subclass differences.
        """
        _, _, _, _, obj5 = setup()
        obj5subclass = FakeSubclass("5", children=obj5.children)
        assert obj5 != obj5subclass
        assert obj5.equal_up_to_subclass(obj5subclass)
        assert obj5subclass.equal_up_to_subclass(obj5)

    def t_equal_child_independent_attrs(self):
        """
        Child-independent attributes should be equal here.
        """
        _, _, _, _, obj5 = setup()
        obj5subclass = FakeSubclass("5", children=[])
        assert obj5.eq_child_independent_attrs(obj5subclass)

    def t_not_equal_child_independent_attrs_values(self):
        """
        Child-independent attributes should not be equal here.
        """
        _, _, _, _, obj5 = setup()
        obj5subclass = FakeSubclass("6", children=[])
        assert not obj5.eq_child_independent_attrs(obj5subclass)

    def t_not_equal_child_independent_attrs_names(self):
        """
        Child-independent attributes should not be equal here.
        """
        # FakeSubclass2 has an extra attribute 'extra_attr'
        _, _, _, _, obj5 = setup()
        obj5subclass = FakeSubclass2("5", children=[])
        assert not obj5.eq_child_independent_attrs(obj5subclass)


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

    def t_replace_all_multiple_replacements_positions_none(self):
        """
        Should replace old (all) instances of obj1 with obj2 and old instances of
        obj2 with obj3 in obj5.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2, obj2: obj3})
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[
                                FakePylogicObject("2"),
                                FakePylogicObject(
                                    "3",
                                    children=[
                                        FakePylogicObject("1"),
                                        FakePylogicObject("2"),
                                    ],
                                ),
                            ],
                        ),
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("1"), FakePylogicObject("2")],
                        ),
                    ],
                ),
                FakePylogicObject("2"),
                FakePylogicObject(
                    "3",
                    children=[
                        FakePylogicObject("2"),
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("1"), FakePylogicObject("2")],
                        ),
                    ],
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_all_cyclic_replacements_positions_none(self):
        """
        Should permute the replacements in a cyclic manner, replacing obj1 with obj2
        and obj2 with obj1 in obj5.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2, obj2: obj1})
        assert new_obj == FakePylogicObject(
            "5",
            children=[
                FakePylogicObject(
                    "4",
                    children=[
                        FakePylogicObject(
                            "3",
                            children=[FakePylogicObject("2"), FakePylogicObject("1")],
                        ),
                        FakePylogicObject("1"),
                    ],
                ),
                FakePylogicObject("2"),
                FakePylogicObject(
                    "3", children=[FakePylogicObject("2"), FakePylogicObject("1")]
                ),
            ],
        )
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_positions_single_empty_root_not_key(self):
        """
        Should replace only the root object if it matches (not in this case).
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
        assert new_obj == obj5

    def t_replace_positions_single_empty_root_in_keys(self):
        """
        Should replace only the root object if it matches.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj5: obj2}, positions=[[]])
        assert new_obj == FakePylogicObject("2")
        assert obj5.children == [obj4, obj1, obj3]

    def t_replace_positions_has_empty_root_not_key(self):
        """
        Should replace according to the dict and positions.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj1: obj2}, positions=[[], [0]])
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

    def t_replace_positions_has_empty_root_in_keys(self):
        """
        Should replace according to the dict and positions.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj5: obj2, obj1: obj2}, positions=[[0], []])
        assert new_obj == FakePylogicObject("2")
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

    def t_replace_positions_empty_root_in_keys(self):
        """
        Should not replace anything.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({obj5: obj2}, positions=[])
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

    def t_replace_all_positions_empty_dict(self):
        """
        Should not replace anything.
        """
        obj1, obj2, obj3, obj4, obj5 = setup()
        new_obj = obj5.replace({})
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


class TestDictConstruction:
    def t_to_dict(self):
        """
        Should convert the object to a dictionary representation.
        """
        _, _, _, _, obj5 = setup()
        expected_dict = {
            "children": [
                {
                    "children": [
                        {
                            "children": [
                                {
                                    "children": [],
                                    "leaves": [],
                                    "name": "1",
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                },
                                {
                                    "children": [],
                                    "leaves": [],
                                    "name": "2",
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                },
                            ],
                            "leaves": [
                                {
                                    "children": [],
                                    "leaves": [],
                                    "name": "1",
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                },
                                {
                                    "children": [],
                                    "leaves": [],
                                    "name": "2",
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                },
                            ],
                            "name": "3",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "leaves": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                    ],
                    "leaves": [
                        {
                            "children": [],
                            "leaves": [],
                            "name": "1",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "leaves": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "leaves": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                    ],
                    "name": "4",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "leaves": [],
                    "name": "1",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [
                        {
                            "children": [],
                            "leaves": [],
                            "name": "1",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "leaves": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                    ],
                    "leaves": [
                        {
                            "children": [],
                            "leaves": [],
                            "name": "1",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "leaves": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                    ],
                    "name": "3",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
            ],
            "leaves": [
                {
                    "children": [],
                    "leaves": [],
                    "name": "1",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "leaves": [],
                    "name": "2",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "leaves": [],
                    "name": "2",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "leaves": [],
                    "name": "1",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "leaves": [],
                    "name": "1",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "leaves": [],
                    "name": "2",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
            ],
            "name": "5",
            "class_module": "pylogic_tests.base",
            "class_name": "FakePylogicObject",
        }
        assert obj5.to_dict() == expected_dict

    def t_from_dict(self):
        """
        Should create an object from a dictionary representation.
        """
        _, _, _, _, obj5 = setup()
        dict_ = {
            "children": [
                {
                    "children": [
                        {
                            "children": [
                                {
                                    "children": [],
                                    "name": "1",
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                },
                                {
                                    "children": [],
                                    "name": "2",
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                },
                            ],
                            "name": "3",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                    ],
                    "name": "4",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [],
                    "name": "1",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
                {
                    "children": [
                        {
                            "children": [],
                            "name": "1",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                        {
                            "children": [],
                            "name": "2",
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                        },
                    ],
                    "name": "3",
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                },
            ],
            "name": "5",
            "class_module": "pylogic_tests.base",
            "class_name": "FakePylogicObject",
        }
        new_obj = FakePylogicObject.from_dict(dict_)
        assert new_obj == obj5

    def t_dict_to_constructor_kwargs(self):
        """
        Should convert a dictionary representation to constructor arguments.
        """
        _, _, _, _, obj5 = setup()
        dict_ = {
            "class_module": "pylogic_tests.base",
            "class_name": "FakePylogicObject",
            "name": "5",
            "children": [
                {
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                    "name": "4",
                    "children": [
                        {
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                            "name": "3",
                            "children": [
                                {
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                    "name": "1",
                                    "children": [],
                                },
                                {
                                    "class_module": "pylogic_tests.base",
                                    "class_name": "FakePylogicObject",
                                    "name": "2",
                                    "children": [],
                                },
                            ],
                        },
                        {
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                            "name": "2",
                            "children": [],
                        },
                    ],
                },
                {
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                    "name": "1",
                    "children": [],
                },
                {
                    "class_module": "pylogic_tests.base",
                    "class_name": "FakePylogicObject",
                    "name": "3",
                    "children": [
                        {
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                            "name": "1",
                            "children": [],
                        },
                        {
                            "class_module": "pylogic_tests.base",
                            "class_name": "FakePylogicObject",
                            "name": "2",
                            "children": [],
                        },
                    ],
                },
            ],
        }
        kwargs = FakePylogicObject.dict_to_constructor_kwargs(dict_)
        assert kwargs == {
            "name": "5",
            "children": [
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
        }


class TestUnify:
    """
    Basic object = object that can serve as a key in the unification dict.
    By default, basic objects are objects with no children. Can be modified with
    the `key_check` parameter.

    Complex object = not a basic object.
    """

    def t_eq_basic(self):
        """
        Should unify two objects that are equal.
        """
        obj1 = FakePylogicObject("1")
        obj1b = FakePylogicObject("1")
        unified = obj1.unify(obj1b)
        assert bool(unified)
        assert unified == {}

    def t_eq_complex(self):
        """
        Should unify two objects that are equal.
        """
        obj1 = FakePylogicObject("1")
        obj2 = FakePylogicObject("2", children=[obj1])
        obj2b = FakePylogicObject("2", children=[obj1])
        unified = obj2.unify(obj2b)
        assert bool(unified)
        assert unified == {}

    def t_basic_to_complex(self):
        """
        basic.unify(complex) should return {basic: complex}
        """
        obj1 = FakePylogicObject("1")
        obj2 = FakePylogicObject("2", children=[obj1])
        obj3 = FakePylogicObject("3", children=[obj1, obj2])
        obj4 = FakePylogicObject("4")
        unified = obj4.unify(obj3)
        assert unified == {obj4: obj3}

    def t_no_basic_on_lhs(self):
        """
        If `unify` is called on something that has no basic objects, should
        return `None`.
        """
        obj1 = FakePylogicObject("1")
        obj2 = FakePylogicObject("2", children=[obj1])
        obj3 = FakePylogicObject("3", children=[obj1, obj2])
        obj4 = FakePylogicObject("4")
        unified = obj4.unify(obj3, key_check=lambda o: o.name == "1")  # type: ignore
        assert unified is None

    def t_complex_unification(self):
        """
        Should find a unification, if possible.
        """
        # obj1 unifies to obj1b but should not be included in the unification dict
        # because they are equal.
        obj1 = FakePylogicObject("1")
        obj2 = FakePylogicObject("2")
        obj3 = FakePylogicObject("3")
        obj4 = FakePylogicObject("4", children=[obj2, obj3])
        obj5 = FakePylogicObject("5", children=[obj4, obj1])

        obj1b = FakePylogicObject("1")
        objd = FakePylogicObject("d")
        obje = FakePylogicObject("e")
        objf = FakePylogicObject("f")
        objg = FakePylogicObject("g")
        objh = FakePylogicObject("h")
        objb = FakePylogicObject("b", children=[objd, obje, objf])
        objc = FakePylogicObject("c", children=[objg, objh])
        obj4b = FakePylogicObject("4", children=[objb, objc])
        obj5b = FakePylogicObject("5", children=[obj4b, obj1b])

        unified = obj5.unify(obj5b)
        assert unified == {obj2: objb, obj3: objc}

    def t_complex_unification_different_keycheck(self):
        """
        Should find a unification, if possible, with a different `key_check`
        parameter.
        """
        var_obj1 = FakePylogicObject("var_1")
        obj2 = FakePylogicObject("2")
        obj3 = FakePylogicObject("3")
        var_obj4 = FakePylogicObject("var_4", children=[obj2, obj3])
        obj5 = FakePylogicObject("5", children=[var_obj4, var_obj1])

        obj1b = FakePylogicObject("1")
        objd = FakePylogicObject("d")
        obje = FakePylogicObject("e")
        objf = FakePylogicObject("f")
        objg = FakePylogicObject("g")
        objh = FakePylogicObject("h")
        objb = FakePylogicObject("b", children=[objd, obje, objf])
        objc = FakePylogicObject("c", children=[objg, objh])
        obj4b = FakePylogicObject("4", children=[objb, objc])
        obj5b = FakePylogicObject("5", children=[obj4b, obj1b])

        unified = obj5.unify(obj5b, key_check=lambda o: o.name.startswith("var_"))  # type: ignore
        assert unified == {var_obj1: obj1b, var_obj4: obj4b}

    def t_complex_unification_impossible(self):
        """
        Should find a unification, if possible (not in this case).
        """
        obj1 = FakePylogicObject("1")
        obj2 = FakePylogicObject("2")
        obj3 = FakePylogicObject("3")
        obj4 = FakePylogicObject("4", children=[obj2, obj3])
        obj5 = FakePylogicObject("5", children=[obj4, obj1])

        obj1b = FakePylogicObject("1")
        objd = FakePylogicObject("d")
        obje = FakePylogicObject("e")
        objf = FakePylogicObject("f")
        objg = FakePylogicObject("g")
        objh = FakePylogicObject("h")
        obji = FakePylogicObject("i")  # extra child
        objb = FakePylogicObject("b", children=[objd, obje, objf])
        objc = FakePylogicObject("c", children=[objg, objh])
        obj4b = FakePylogicObject("4", children=[objb, objc, obji])
        obj5b = FakePylogicObject("5", children=[obj4b, obj1b])

        unified = obj5.unify(obj5b)
        assert unified is None

    def t_unification_replacement(self):
        """
        Check that unification followed by replacement works as expected.
        ```
        unif = a.unify(b)
        a.replace(unif) == b
        ```
        """
        # obj1 unifies to obj1b but should not be included in the unification dict
        # because they are equal.
        obj1 = FakePylogicObject("1")
        obj2 = FakePylogicObject("2")
        obj3 = FakePylogicObject("3")
        obj4 = FakePylogicObject("4", children=[obj2, obj3])
        obj5 = FakePylogicObject("5", children=[obj4, obj1])

        obj1b = FakePylogicObject("1")
        objd = FakePylogicObject("d")
        obje = FakePylogicObject("e")
        objf = FakePylogicObject("f")
        objg = FakePylogicObject("g")
        objh = FakePylogicObject("h")
        objb = FakePylogicObject("b", children=[objd, obje, objf])
        objc = FakePylogicObject("c", children=[objg, objh])
        obj4b = FakePylogicObject("4", children=[objb, objc])
        obj5b = FakePylogicObject("5", children=[obj4b, obj1b])

        unified = obj5.unify(obj5b)
        assert unified == {obj2: objb, obj3: objc}
        assert obj5.replace(unified) == obj5b  # type: ignore
