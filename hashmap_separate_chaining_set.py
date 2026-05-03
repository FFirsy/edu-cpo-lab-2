from typing import Any, Callable, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar

T = TypeVar("T")
S = TypeVar("S")


class HashMapSeparateChainingSet(Generic[T]):
    """
    Immutable set based on hash map with separate chaining.

    All operations return a new set without modifying the original.
    Uses structural sharing where possible to avoid unnecessary copying.
    """

    def __init__(self, capacity: int = 16, load_factor: float = 0.75):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        if not (0 < load_factor <= 1):
            raise ValueError("load_factor must be in (0, 1]")
        self._capacity = capacity
        self._load_factor = load_factor
        self._buckets: Tuple[Tuple[T, ...], ...] = tuple(tuple() for _ in range(capacity))
        self._size = 0

    def _hash(self, element: T) -> int:
        return hash(element) % self._capacity

    def _copy_with(
        self,
        buckets: Optional[Tuple[Tuple[T, ...], ...]] = None,
        capacity: Optional[int] = None,
        size: Optional[int] = None,
    ) -> "HashMapSeparateChainingSet[T]":
        """Create a new set, reusing self's fields where not overridden."""
        result = HashMapSeparateChainingSet.__new__(HashMapSeparateChainingSet)
        result._capacity = capacity if capacity is not None else self._capacity
        result._load_factor = self._load_factor
        result._buckets = buckets if buckets is not None else self._buckets
        result._size = size if size is not None else self._size
        return result

    def _needs_resize(self, extra: int = 0) -> bool:
        return (self._size + extra) / self._capacity > self._load_factor

    def _resized(self) -> "HashMapSeparateChainingSet[T]":
        """Return a new set with capacity doubled and all elements rehashed."""
        new_capacity = self._capacity * 2
        new_buckets: List[Tuple[T, ...]] = [tuple() for _ in range(new_capacity)]
        for bucket in self._buckets:
            for elem in bucket:
                idx = hash(elem) % new_capacity
                new_buckets[idx] = new_buckets[idx] + (elem,)
        return self._copy_with(buckets=tuple(new_buckets), capacity=new_capacity)

    def _ensure_capacity(self, extra: int = 0) -> "HashMapSeparateChainingSet[T]":
        """Return a set with enough capacity; resize if needed."""
        if self._needs_resize(extra):
            return self._resized()
        return self

    # ---------- pure function helpers (recursive) ----------

    def _elem_in_bucket(self, element: T, bucket: Tuple[T, ...]) -> bool:
        """Recursively check if element is in bucket."""
        if len(bucket) == 0:
            return False
        if bucket[0] == element:
            return True
        return self._elem_in_bucket(element, bucket[1:])

    def _remove_from_bucket(self, element: T, bucket: Tuple[T, ...]) -> Tuple[T, ...]:
        """Recursively remove element from bucket; return new bucket."""
        if len(bucket) == 0:
            return tuple()
        if bucket[0] == element:
            return bucket[1:]
        return (bucket[0],) + self._remove_from_bucket(element, bucket[1:])

    def _bucket_to_list(self, bucket: Tuple[T, ...]) -> List[T]:
        """Recursively convert bucket to list."""
        if len(bucket) == 0:
            return []
        return [bucket[0]] + self._bucket_to_list(bucket[1:])

    def _all_elements(self, buckets: Tuple[Tuple[T, ...], ...]) -> List[T]:
        """Recursively collect all elements from all buckets."""
        if len(buckets) == 0:
            return []
        return self._bucket_to_list(buckets[0]) + self._all_elements(buckets[1:])

    def _filter_bucket(self, bucket: Tuple[T, ...], predicate: Callable[[T], bool]) -> Tuple[T, ...]:
        """Recursively filter a bucket."""
        if len(bucket) == 0:
            return tuple()
        if predicate(bucket[0]):
            return (bucket[0],) + self._filter_bucket(bucket[1:], predicate)
        return self._filter_bucket(bucket[1:], predicate)

    def _map_bucket(self, bucket: Tuple[T, ...], func: Callable[[T], Any]) -> List[Any]:
        """Recursively map over a bucket; return list (may have duplicates after map)."""
        if len(bucket) == 0:
            return []
        return [func(bucket[0])] + self._map_bucket(bucket[1:], func)

    def _reduce_bucket(
        self, bucket: Tuple[T, ...], func: Callable[[S, T], S], acc: S
    ) -> S:
        """Recursively reduce a bucket."""
        if len(bucket) == 0:
            return acc
        return self._reduce_bucket(bucket[1:], func, func(acc, bucket[0]))

    # ---------- public immutable API (instance methods) ----------

    def cons(self, element: T) -> "HashMapSeparateChainingSet[T]":
        """Return a new set with element added."""
        ensured = self._ensure_capacity(1)
        idx = hash(element) % ensured._capacity
        bucket = ensured._buckets[idx]
        if self._elem_in_bucket(element, bucket):
            return ensured  # unchanged
        new_buckets = list(ensured._buckets)
        new_buckets[idx] = bucket + (element,)
        return ensured._copy_with(buckets=tuple(new_buckets), size=ensured._size + 1)

    def remove(self, element: T) -> "HashMapSeparateChainingSet[T]":
        """Return a new set with element removed."""
        idx = hash(element) % self._capacity
        bucket = self._buckets[idx]
        if not self._elem_in_bucket(element, bucket):
            return self  # unchanged
        new_buckets = list(self._buckets)
        new_buckets[idx] = self._remove_from_bucket(element, bucket)
        return self._copy_with(buckets=tuple(new_buckets), size=self._size - 1)

    def member(self, element: T) -> bool:
        idx = hash(element) % self._capacity
        return self._elem_in_bucket(element, self._buckets[idx])

    def length(self) -> int:
        return self._size

    def to_list(self) -> List[T]:
        return self._all_elements(self._buckets)

    def from_list(self, lst: Iterable[T]) -> "HashMapSeparateChainingSet[T]":
        """Return a new set built from a Python iterable."""
        result = empty()
        for elem in lst:
            result = cons(result, elem)
        return result

    def filter(self, predicate: Callable[[T], bool]) -> "HashMapSeparateChainingSet[T]":
        """Return a new set with only elements satisfying predicate."""
        new_buckets: List[Tuple[T, ...]] = [
            self._filter_bucket(bucket, predicate) for bucket in self._buckets
        ]
        new_size = sum(len(b) for b in new_buckets)
        return self._copy_with(buckets=tuple(new_buckets), size=new_size)

    def map(self, func: Callable[[T], Any]) -> "HashMapSeparateChainingSet[Any]":
        """Return a new set by applying func to each element (may collapse duplicates)."""
        result: List[Any] = []
        for bucket in self._buckets:
            result.extend(self._map_bucket(bucket, func))
        # Deduplicate while preserving order
        seen: List[Any] = []
        for v in result:
            if v not in seen:
                seen.append(v)
        return from_list(seen)

    def reduce(
        self, func: Callable[[S, T], S], initial: Optional[S] = None
    ) -> S:
        """Reduce all elements with func, starting from initial."""
        buckets = self._buckets
        if initial is None:
            if self._size == 0:
                raise TypeError("reduce of empty set with no initial value")
            # Find first element to use as initial accumulator
            for i, bucket in enumerate(buckets):
                if len(bucket) > 0:
                    acc: S = bucket[0]
                    # Reduce remaining elements in this bucket
                    acc = self._reduce_bucket(bucket[1:], func, acc)
                    # Reduce all remaining buckets (start from i+1)
                    return self._reduce_remaining_buckets(buckets, i + 1, func, acc)
            raise TypeError("reduce of empty set with no initial value")
        else:
            acc: S = initial
            return self._reduce_all_buckets(buckets, 0, func, acc)

    def _reduce_remaining_buckets(
        self, buckets: Tuple[Tuple[T, ...], ...], start_idx: int, func: Callable[[S, T], S], acc: S
    ) -> S:
        """Reduce buckets starting from start_idx (skip already-processed buckets)."""
        if start_idx >= len(buckets):
            return acc
        acc = self._reduce_bucket(buckets[start_idx], func, acc)
        return self._reduce_remaining_buckets(buckets, start_idx + 1, func, acc)

    def _reduce_all_buckets(
        self, buckets: Tuple[Tuple[T, ...], ...], idx: int, func: Callable[[S, T], S], acc: S
    ) -> S:
        if idx >= len(buckets):
            return acc
        acc = self._reduce_bucket(buckets[idx], func, acc)
        return self._reduce_all_buckets(buckets, idx + 1, func, acc)

    def intersection(self, other: "HashMapSeparateChainingSet[T]") -> "HashMapSeparateChainingSet[T]":
        """Return a new set with elements present in both sets."""
        result = empty()
        for elem in self._all_elements(self._buckets):
            if other.member(elem):
                result = cons(result, elem)
        return result

    def concat(self, other: "HashMapSeparateChainingSet[T]") -> "HashMapSeparateChainingSet[T]":
        """Return a new set containing all elements from both sets."""
        result = self
        for elem in other._all_elements(other._buckets):
            result = cons(result, elem)
        return result

    def __iter__(self) -> Iterator[T]:
        """Return an iterator over all elements."""
        elements = self._all_elements(self._buckets)
        idx = 0
        while idx < len(elements):
            yield elements[idx]
            idx += 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HashMapSeparateChainingSet):
            return False
        if self._size != other._size:
            return False
        for elem in self:
            if not other.member(elem):
                return False
        return True

    def __str__(self) -> str:
        elements = self.to_list()
        if len(elements) == 0:
            return "{}"
        return "{" + ",".join(str(e) for e in elements) + "}"


# ---------- function-style API ----------


def empty() -> HashMapSeparateChainingSet[Any]:
    """Return an empty immutable set."""
    return HashMapSeparateChainingSet()


def cons(s: HashMapSeparateChainingSet[T], element: T) -> HashMapSeparateChainingSet[T]:
    """Function-style cons: return a new set with element added."""
    return s.cons(element)


def remove(s: HashMapSeparateChainingSet[T], element: T) -> HashMapSeparateChainingSet[T]:
    """Function-style remove: return a new set with element removed."""
    return s.remove(element)


def member(s: HashMapSeparateChainingSet[T], element: T) -> bool:
    """Function-style member check."""
    return s.member(element)


def length(s: HashMapSeparateChainingSet[T]) -> int:
    """Function-style length."""
    return s.length()


def to_list(s: HashMapSeparateChainingSet[T]) -> List[T]:
    """Function-style to_list."""
    return s.to_list()


def from_list(lst: Iterable[T]) -> HashMapSeparateChainingSet[T]:
    """Function-style from_list: build a set from a Python iterable."""
    result: HashMapSeparateChainingSet[T] = empty()
    for elem in lst:
        result = cons(result, elem)
    return result


def filter_set(s: HashMapSeparateChainingSet[T], predicate: Callable[[T], bool]) -> HashMapSeparateChainingSet[T]:
    """Function-style filter."""
    return s.filter(predicate)


def map_set(s: HashMapSeparateChainingSet[T], func: Callable[[T], Any]) -> HashMapSeparateChainingSet[Any]:
    """Function-style map."""
    return s.map(func)


def reduce_set(
    s: HashMapSeparateChainingSet[T], func: Callable[[S, T], S], initial: Optional[S] = None
) -> S:
    """Function-style reduce."""
    return s.reduce(func, initial)


def intersection(
    s1: HashMapSeparateChainingSet[T], s2: HashMapSeparateChainingSet[T]
) -> HashMapSeparateChainingSet[T]:
    """Function-style intersection."""
    return s1.intersection(s2)


def concat(
    s1: HashMapSeparateChainingSet[T], s2: HashMapSeparateChainingSet[T]
) -> HashMapSeparateChainingSet[T]:
    """Function-style concat (monoid)."""
    return s1.concat(s2)


def find(s: HashMapSeparateChainingSet[T], predicate: Callable[[T], bool]) -> Optional[T]:
    """Find first element satisfying predicate."""
    for elem in s:
        if predicate(elem):
            return elem
    return None


def iterator(s: HashMapSeparateChainingSet[T]) -> Iterator[T]:
    """Return an iterator over the set."""
    return iter(s)


def reverse(s: HashMapSeparateChainingSet[T]) -> HashMapSeparateChainingSet[T]:
    """
    Reverse is a no-op for unordered sets,
    but we return a new set with the same elements.
    """
    return from_list(s.to_list())
