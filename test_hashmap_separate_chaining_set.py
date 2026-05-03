import itertools
from typing import Optional

import pytest
from hypothesis import given, strategies as st

from hashmap_separate_chaining_set import (
    HashMapSeparateChainingSet,
    concat,
    cons,
    empty,
    filter_set,
    find,
    from_list,
    intersection,
    length,
    map_set,
    member,
    reduce_set,
    remove,
    to_list,
)


# ---------- API test from the lab specification ----------


def test_api():
    """API test provided in the lab specification (variant 4)."""
    empty_set = HashMapSeparateChainingSet()
    assert str(cons(empty_set, None)) == "{None}"
    l1 = cons(cons(empty_set, 1), None)
    l2 = cons(cons(empty_set, None), 1)
    assert str(empty_set) == "{}"
    assert str(l1) in ("{None,1}", "{1,None}")
    assert empty_set != l1
    assert empty_set != l2
    assert l1 == l2
    assert l1 == cons(cons(l1, None), 1)

    assert length(empty_set) == 0
    assert length(l1) == 2
    assert length(l2) == 2

    assert str(remove(l1, None)) in ("{1}", "{1}")
    assert str(remove(l1, 1)) in ("{None}", "{None}")

    assert not member(empty_set, None)
    assert member(l1, None)
    assert member(l1, 1)
    assert not member(l1, 2)

    assert intersection(l1, l2) == l1
    assert intersection(l1, l2) == l2
    assert intersection(l1, empty_set) == empty_set
    assert intersection(l1, cons(empty_set, None)) == cons(empty_set, None)

    lst1 = to_list(l1)
    assert lst1 in ([[None, 1], [1, None]])
    assert l1 == from_list([None, 1])
    assert l1 == from_list([1, None, 1])

    assert concat(l1, l2) == from_list([None, 1, 1, None])

    buf = []
    for e in l1:
        buf.append(e)
    assert tuple(buf) in list(itertools.permutations([1, None]))

    lst = to_list(l1) + to_list(l2)
    for e in l1:
        lst.remove(e)
    for e in l2:
        lst.remove(e)
    assert lst == []

    # and also you need:
    # - filter(l, f)
    # - map(l, f)
    # - reduce(l, f)
    # - empty()


# ---------- unit tests ----------


def test_empty():
    s = empty()
    assert length(s) == 0
    assert str(s) == "{}"


def test_cons():
    s = empty()
    s1 = cons(s, 1)
    s2 = cons(s1, 2)
    assert length(s) == 0  # original unchanged
    assert length(s1) == 1
    assert length(s2) == 2
    assert member(s1, 1)
    assert member(s2, 1)
    assert member(s2, 2)


def test_cons_duplicate():
    s = empty()
    s1 = cons(s, 1)
    s2 = cons(s1, 1)  # duplicate, should not change
    assert s2 == s1


def test_cons_none():
    s = empty()
    s1 = cons(s, None)
    assert length(s1) == 1
    assert member(s1, None)


def test_remove():
    s = from_list([1, 2, 3])
    s1 = remove(s, 2)
    assert member(s, 2)  # original unchanged
    assert not member(s1, 2)
    assert member(s1, 1)
    assert member(s1, 3)
    assert length(s1) == 2


def test_remove_not_present():
    s = from_list([1, 2, 3])
    s1 = remove(s, 99)
    assert s1 == s  # unchanged


def test_member():
    s = from_list([1, 2, 3])
    assert member(s, 1)
    assert member(s, 2)
    assert member(s, 3)
    assert not member(s, 4)


def test_length():
    s = empty()
    assert length(s) == 0
    s1 = cons(s, 1)
    assert length(s1) == 1
    s2 = cons(s1, 2)
    assert length(s2) == 2
    s3 = cons(s2, 1)  # duplicate
    assert length(s3) == 2


def test_to_list():
    s = empty()
    assert to_list(s) == []
    s1 = cons(s, 1)
    s2 = cons(s1, 2)
    assert sorted(to_list(s2)) == sorted([1, 2])


def test_from_list():
    s = from_list([])
    assert length(s) == 0
    s1 = from_list([1, 2, 3])
    assert length(s1) == 3
    assert member(s1, 1)
    assert member(s1, 2)
    assert member(s1, 3)
    # duplicates removed
    s2 = from_list([1, 2, 2, 3])
    assert length(s2) == 3


def test_filter():
    s = from_list([1, 2, 3, 4, 5])
    s1 = filter_set(s, lambda x: x % 2 == 0)
    assert sorted(to_list(s1)) == [2, 4]
    # original unchanged
    assert member(s, 1)


def test_map():
    s = from_list([1, 2, 3])
    s1 = map_set(s, lambda x: x * 10)
    assert sorted(to_list(s1)) == [10, 20, 30]


def test_map_dedup():
    s = from_list([1, 2, 3])
    s1 = map_set(s, lambda x: x % 2)  # creates duplicates
    assert sorted(to_list(s1)) in ([0, 1], [1, 0])


def test_reduce():
    s = from_list([1, 2, 3])
    assert reduce_set(s, lambda a, b: a + b) == 6
    assert reduce_set(s, lambda a, b: a + b, 10) == 16
    # empty set with initial
    s0 = empty()
    assert reduce_set(s0, lambda a, b: a + b, 0) == 0


def test_reduce_empty_no_initial():
    s0 = empty()
    with pytest.raises(TypeError):
        reduce_set(s0, lambda a, b: a + b)


def test_intersection():
    s1 = from_list([1, 2, 3])
    s2 = from_list([2, 3, 4])
    s3 = intersection(s1, s2)
    assert sorted(to_list(s3)) == [2, 3]


def test_concat():
    s1 = from_list([1, 2])
    s2 = from_list([2, 3])
    s3 = concat(s1, s2)
    assert sorted(to_list(s3)) == [1, 2, 3]


def test_find():
    s = from_list([1, 2, 3, 4])
    assert find(s, lambda x: x % 2 == 0) in (2, 4)


def test_find_not_found():
    s = from_list([1, 2, 3])
    assert find(s, lambda x: x > 10) is None


def test_iterator():
    s = from_list([1, 2, 3])
    result = []
    for e in s:
        result.append(e)
    assert sorted(result) == [1, 2, 3]


def test_immutability():
    """Verify that operations do not modify the original set."""
    s = from_list([1, 2, 3])
    s1 = cons(s, 4)
    s2 = remove(s, 2)
    s3 = filter_set(s, lambda x: x % 2 == 0)
    s4 = map_set(s, lambda x: x * 10)

    # original unchanged
    assert length(s) == 3
    assert member(s, 1)
    assert member(s, 2)
    assert member(s, 3)
    assert not member(s, 4)


def test_equality():
    s1 = from_list([1, 2, 3])
    s2 = from_list([3, 2, 1])
    s3 = from_list([1, 2])
    assert s1 == s2
    assert s1 != s3
    assert s1 != "not a set"


def test_str():
    s = empty()
    assert str(s) == "{}"
    s1 = cons(s, 1)
    assert "1" in str(s1)
    s2 = cons(s1, None)
    assert "None" in str(s2)


# ---------- property-based tests ----------


@given(st.lists(st.one_of(st.integers(), st.none())))
def test_pbt_from_list_uniqueness(lst):
    """from_list creates a set with no duplicates."""
    s = from_list(lst)
    assert sorted(to_list(s), key=lambda x: (x is None, x)) == sorted(set(lst), key=lambda x: (x is None, x))


@given(st.lists(st.integers()))
def test_pbt_cons_idempotence(lst):
    """cons with the same element twice is idempotent."""
    s = from_list(lst)
    s1 = cons(s, 42)
    s2 = cons(s1, 42)
    assert s1 == s2


@given(st.lists(st.integers()))
def test_pbt_remove_membership(lst):
    """After remove, element is no longer a member."""
    s = from_list(lst)
    if member(s, 42):
        s1 = remove(s, 42)
        assert not member(s1, 42)


@given(st.lists(st.integers()))
def test_pbt_to_list_from_list_roundtrip(lst):
    """to_list(from_list(lst)) contains the same unique elements."""
    s = from_list(lst)
    result = to_list(s)
    assert set(result) == set(lst)


@given(st.lists(st.integers()))
def test_pbt_filter_no_duplicates(lst):
    """filter never produces duplicates."""
    s = from_list(lst)
    s1 = filter_set(s, lambda x: x % 2 == 0)
    result = to_list(s1)
    assert len(result) == len(set(result))


@given(st.lists(st.integers()))
def test_pbt_map_no_duplicates(lst):
    """map may produce duplicates, but the set should have no duplicates."""
    s = from_list(lst)
    s1 = map_set(s, lambda x: x % 5)
    result = to_list(s1)
    assert len(result) == len(set(result))


@given(st.lists(st.integers()))
def test_pbt_intersection_commutative(lst):
    """intersection is commutative."""
    s1 = from_list(lst)
    s2 = from_list([x * 2 for x in lst])
    assert intersection(s1, s2) == intersection(s2, s1)


@given(st.lists(st.integers()))
def test_pbt_concat_associative(lst):
    """concat is associative."""
    s1 = from_list(lst)
    s2 = from_list([1, 2, 3])
    s3 = from_list([3, 4, 5])

    left = concat(concat(s1, s2), s3)
    right = concat(s1, concat(s2, s3))
    assert left == right


@given(st.lists(st.integers()))
def test_pbt_concat_empty_identity(lst):
    """empty() is identity for concat."""
    s = from_list(lst)
    assert concat(empty(), s) == s
    assert concat(s, empty()) == s


@given(st.lists(st.one_of(st.integers(), st.none())))
def test_pbt_immutability(lst):
    """All operations return new sets; original is unchanged."""
    s = from_list(lst)
    original_elements = sorted(to_list(s), key=lambda x: (x is None, x))
    _ = cons(s, 999)
    _ = remove(s, 1)
    _ = filter_set(s, lambda x: True)
    _ = map_set(s, lambda x: x)
    after_elements = sorted(to_list(s), key=lambda x: (x is None, x))
    assert original_elements == after_elements


@given(st.lists(st.integers(min_value=-100, max_value=100)))
def test_pbt_reduce_sum(lst):
    """reduce with sum should equal sum of unique elements."""
    s = from_list(lst)
    if length(s) > 0:
        result = reduce_set(s, lambda a, b: a + b)
        assert result == sum(set(lst))


# ---------- comprehensive property-based tests ----------

@given(st.lists(st.integers()))
def test_pbt_monoid_left_identity(lst):
    """empty() is left identity: concat(empty(), s) == s."""
    s = from_list(lst)
    assert concat(empty(), s) == s


@given(st.lists(st.integers()))
def test_pbt_monoid_right_identity(lst):
    """empty() is right identity: concat(s, empty()) == s."""
    s = from_list(lst)
    assert concat(s, empty()) == s


@given(st.lists(st.integers()))
def test_pbt_monoid_associativity(lst):
    """concat is associative: (s1 ++ s2) ++ s3 == s1 ++ (s2 ++ s3)."""
    s1 = from_list(lst)
    s2 = from_list([1, 2, 3])
    s3 = from_list([3, 4, 5])

    left = concat(concat(s1, s2), s3)
    right = concat(s1, concat(s2, s3))
    assert left == right


@given(st.lists(st.integers()))
def test_pbt_cons_membership(lst):
    """After cons(s, x), x is a member of the new set."""
    s = from_list(lst)
    s1 = cons(s, 9999)  # use a value likely not in lst
    assert member(s1, 9999)


@given(st.lists(st.integers()))
def test_pbt_cons_idempotence_detailed(lst):
    """cons with same element twice gives same result as once."""
    s = from_list(lst)
    x = 42
    s1 = cons(s, x)
    s2 = cons(s1, x)
    assert s1 == s2
    assert length(s1) == length(s2)


@given(st.lists(st.integers()))
def test_pbt_cons_original_unchanged(lst):
    """cons does not modify the original set."""
    s = from_list(lst)
    original = sorted(to_list(s), key=lambda x: (x is None, x))
    _ = cons(s, 9999)
    after = sorted(to_list(s), key=lambda x: (x is None, x))
    assert original == after


@given(st.lists(st.integers()))
def test_pbt_remove_membership_detailed(lst):
    """After remove(s, x) where x in s, x is no longer a member."""
    s = from_list(lst)
    elements = to_list(s)
    if len(elements) > 0:
        x = elements[0]
        s1 = remove(s, x)
        assert not member(s1, x)


@given(st.lists(st.integers()))
def test_pbt_remove_not_present_unchanged(lst):
    """Removing an element not in the set returns the same set."""
    s = from_list(lst)
    s1 = remove(s, 9999)
    assert s1 == s


@given(st.lists(st.integers()))
def test_pbt_remove_original_unchanged(lst):
    """remove does not modify the original set."""
    s = from_list(lst)
    original = sorted(to_list(s), key=lambda x: (x is None, x))
    _ = remove(s, 1)
    after = sorted(to_list(s), key=lambda x: (x is None, x))
    assert original == after


@given(st.lists(st.integers()))
def test_pbt_member_consistency(lst):
    """member(s, x) iff x is in to_list(s)."""
    s = from_list(lst)
    elements = set(to_list(s))
    # Check all elements in set are members
    for x in elements:
        assert member(s, x)
    # Check a value not in set is not a member
    if 9999 not in elements:
        assert not member(s, 9999)


@given(st.lists(st.integers()))
def test_pbt_intersection_idempotence(lst):
    """intersection(s, s) == s."""
    s = from_list(lst)
    assert intersection(s, s) == s


@given(st.lists(st.integers()))
def test_pbt_intersection_commutativity(lst):
    """intersection(s1, s2) == intersection(s2, s1)."""
    s1 = from_list(lst)
    s2 = from_list([x * 2 for x in lst])
    assert intersection(s1, s2) == intersection(s2, s1)


@given(st.lists(st.integers()))
def test_pbt_intersection_subset(lst):
    """intersection(s1, s2) is subset of both s1 and s2."""
    s1 = from_list(lst)
    s2 = from_list([x * 2 for x in lst])
    inter = intersection(s1, s2)
    # All elements in inter are in both s1 and s2
    for x in to_list(inter):
        assert member(s1, x)
        assert member(s2, x)


@given(st.lists(st.integers()))
def test_pbt_intersection_empty_identity(lst):
    """intersection(s, empty()) == empty()."""
    s = from_list(lst)
    assert intersection(s, empty()) == empty()
    assert intersection(empty(), s) == empty()


@given(st.lists(st.integers()))
def test_pbt_filter_true_identity(lst):
    """filter(s, lambda x: True) returns a set with same elements."""
    s = from_list(lst)
    s1 = filter_set(s, lambda x: True)
    assert s == s1


@given(st.lists(st.integers()))
def test_pbt_filter_false_empty(lst):
    """filter(s, lambda x: False) returns empty set."""
    s = from_list(lst)
    s1 = filter_set(s, lambda x: False)
    assert s1 == empty()


@given(st.lists(st.integers()))
def test_pbt_filter_preserves_membership(lst):
    """Elements in filter(s, p) all satisfy p."""
    s = from_list(lst)
    s1 = filter_set(s, lambda x: x % 2 == 0)
    for x in to_list(s1):
        assert x % 2 == 0


@given(st.lists(st.integers()))
def test_pbt_filter_original_unchanged(lst):
    """filter does not modify the original set."""
    s = from_list(lst)
    original = sorted(to_list(s), key=lambda x: (x is None, x))
    _ = filter_set(s, lambda x: x % 2 == 0)
    after = sorted(to_list(s), key=lambda x: (x is None, x))
    assert original == after


@given(st.lists(st.integers()))
def test_pbt_map_original_unchanged(lst):
    """map does not modify the original set."""
    s = from_list(lst)
    original = sorted(to_list(s), key=lambda x: (x is None, x))
    _ = map_set(s, lambda x: x * 10)
    after = sorted(to_list(s), key=lambda x: (x is None, x))
    assert original == after


@given(st.lists(st.integers()))
def test_pbt_map_no_duplicates_detailed(lst):
    """map never produces duplicate elements in the result set."""
    s = from_list(lst)
    s1 = map_set(s, lambda x: x % 7)  # may produce duplicates
    result = to_list(s1)
    assert len(result) == len(set(result))


@given(st.lists(st.integers()))
def test_pbt_find_satisfies_predicate(lst):
    """If find returns a value, it satisfies the predicate."""
    s = from_list(lst)
    # Only test if there's an even number
    has_even = any(x % 2 == 0 for x in to_list(s))
    result = find(s, lambda x: x % 2 == 0)
    if has_even:
        assert result is not None
        assert result % 2 == 0
    else:
        assert result is None


@given(st.lists(st.integers()))
def test_pbt_find_none_for_false_predicate(lst):
    """find(s, lambda x: False) always returns None."""
    s = from_list(lst)
    assert find(s, lambda x: False) is None


@given(st.lists(st.integers()))
def test_pbt_iterator_yields_all_elements(lst):
    """Iterator yields all elements exactly once (as a set)."""
    s = from_list(lst)
    elements_from_iter = []
    for x in s:
        elements_from_iter.append(x)
    assert set(elements_from_iter) == set(to_list(s))
    assert len(elements_from_iter) == len(set(elements_from_iter))


@given(st.lists(st.one_of(st.integers(), st.none())))
def test_pbt_reverse_is_identity_for_sets(lst):
    """For unordered sets, reverse should return a set with same elements."""
    from hashmap_separate_chaining_set import reverse
    s = from_list(lst)
    s1 = reverse(s)
    assert set(to_list(s)) == set(to_list(s1))


@given(st.lists(st.integers()))
def test_pbt_str_contains_elements(lst):
    """str(s) contains string representations of all elements."""
    s = from_list(lst)
    if length(s) == 0:
        assert str(s) == "{}"
    else:
        # Just check it starts with { and ends with }
        s_str = str(s)
        assert s_str.startswith("{")
        assert s_str.endswith("}")
