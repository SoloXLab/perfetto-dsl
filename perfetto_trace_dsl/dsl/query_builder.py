"""
Backward-compatible query builder exports.
"""

from .slice_query_builder import (
    Flow,
    RelatedObjectsAccessor,
    Slice,
    SliceQueryBuilder,
    Track,
)

QueryBuilder = SliceQueryBuilder

__all__ = [
    "QueryBuilder",
    "SliceQueryBuilder",
    "Slice",
    "Track",
    "Flow",
    "RelatedObjectsAccessor",
]
