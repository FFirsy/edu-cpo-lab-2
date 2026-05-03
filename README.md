
# Lab 2 - Immutable HashMap Separate Chaining Set

This project implements an **immutable set** using a hash map with separate chaining.

All operations return a **new set** without modifying the original, making it safe for multi-threaded programming and functional-style code.

## Project Structure

- `hashmap_separate_chaining_set.py` - Immutable set implementation
- `test_hashmap_separate_chaining_set.py` - Unit and property-based tests
- `requirements.txt` - Python dependencies

## Features

- **Immutable operations** - `cons`, `remove`, `filter`, `map`, `concat` all return new sets
- **Structural sharing** - unchanged buckets are shared between old and new sets to avoid unnecessary copying
- **Separate chaining** - Each bucket is a tuple (immutable); dynamic resizing when load factor exceeds 0.75
- **Recursion-based implementation** - All operations use recursion instead of loops
- **Full API support**:
  - `cons(s, elem)` - add element
  - `remove(s, elem)` - remove element
  - `member(s, elem)` - membership test
  - `length(s)` - size
  - `to_list(s)` / `from_list(lst)` - conversion
  - `filter_set(s, pred)` - filter
  - `map_set(s, f)` - map
  - `reduce_set(s, f, init)` - reduce
  - `find(s, pred)` - find element
  - `intersection(s1, s2)` - set intersection
  - `concat(s1, s2)` - set union (monoid)
  - `iterator(s)` - iterator
  - `empty()` - empty set (monoid identity)
  - `reverse(s)` - no-op for unordered set
- **Handles special values** - `None` is accepted; mixed types supported
- **Property-based tests** - Using Hypothesis to verify invariants

## Design Notes

### Immutability

The set is implemented as a immutable data structure. The internal representation uses:
- `_buckets: Tuple[Tuple[T, ...], ...]` - a tuple of immutable buckets
- Each bucket is a tuple of elements (immutable)

When an operation modifies the set:
1. A new set instance is created
2. Only the affected bucket is rebuilt
3. All other buckets are **shared** with the previous version (structural sharing)

### Recursion

All iterative operations are implemented using recursion:
- `_elem_in_bucket` - check membership in a bucket
- `_remove_from_bucket` - remove element from bucket
- `_bucket_to_list` - convert bucket to list
- `_all_elements` - collect all elements
- `_filter_bucket` - filter a bucket
- `_map_bucket` - map over a bucket
- `_reduce_bucket` - reduce a bucket

### Resizing

When `size / capacity > load_factor` (0.75), capacity doubles.
All elements are rehashed into new buckets.

### Comparison with Mutable Version (Lab 1)

| Feature | Mutable (Lab 1) | Immutable (Lab 2) |
|---------|-------------------|---------------------|
| Add     | `s.add(x)` modifies `s` | `s1 = cons(s, x)` returns new set |
| Remove  | `s.remove(x)` modifies `s` | `s1 = remove(s, x)` returns new set |
| Memory  | Single copy | Structural sharing reduces copying |
| Thread-safe | No | Yes (no mutations) |


## Contributors

- Liu Xuhan - Implementation
- Wang Qifan - Tests and documentation

## Changelog

- **2026-05-03** - Initial implementation of immutable hash map separate chaining set
