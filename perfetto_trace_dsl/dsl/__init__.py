"""
Perfetto DSL - Chainable DSL for Perfetto trace analysis
"""

from .trace import Trace
from .slice_query_builder import Slice, Track, Flow, SliceQueryBuilder, RelatedObjectsAccessor
from .counter_query_builder import Counter, CounterQueryBuilder
from .cpu_freq_query_builder import CpuFreqQueryBuilder, CpuFreqData
from .cpu_usage_query_builder import CpuUsageQueryBuilder, CpuUsageData
from .metric_query_builder import MetricQueryBuilder

# Backward-compatible alias used by existing callers/tests.
QueryBuilder = SliceQueryBuilder

__all__ = [
    "Trace",
    "Slice", 
    "Counter",
    "CounterQueryBuilder",
    "Track",
    "Flow",
    "QueryBuilder",
    "SliceQueryBuilder",
    "RelatedObjectsAccessor",
    "CpuFreqQueryBuilder",
    "CpuFreqData",
    "CpuUsageQueryBuilder",
    "CpuUsageData",
    "MetricQueryBuilder"
]
