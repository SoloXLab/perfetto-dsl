import types
from unittest.mock import Mock

from perfetto_trace_dsl.dsl import FlowLink, QueryBuilder, Slice


class _Row:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class _MockProcessor:
    def __init__(self):
        self.last_sql = None

    def query(self, sql):
        self.last_sql = sql
        return []


def _make_slice(slice_id: int, ts: int, dur: int) -> Slice:
    return Slice(
        id=slice_id,
        name=f"s{slice_id}",
        ts=ts,
        dur=dur,
        pid=1,
        tid=1,
        cat="cat",
        track_id=1,
    )


def test_openspec_chain_filters_and_arg_compare():
    processor = _MockProcessor()
    builder = QueryBuilder(processor)

    builder.slice().id(123).name("doFrame").ts(">=", 1000).dur("<", 5000).depth(">=", 1)
    builder.arg("frame_id").compare("==", 347)

    assert "slice.id = 123" in builder.where_conditions
    assert "slice.name = 'doFrame'" in builder.where_conditions
    assert "slice.ts >= 1000" in builder.where_conditions
    assert "slice.dur < 5000" in builder.where_conditions
    assert "slice.depth >= 1" in builder.where_conditions
    assert any("args_cmp_" in join for join in builder.joins)
    assert any("frame_id" in condition for condition in builder.where_conditions)


def test_openspec_slice_sugar_supports_tuple_and_args():
    processor = _MockProcessor()
    builder = QueryBuilder(processor)

    builder.slice(
        id=123,
        name="doFrame",
        ts=(">=", 1000),
        dur=("<", 5000),
        depth=(">=", 1),
        args={"frame_id": 347},
    )

    assert "slice.id = 123" in builder.where_conditions
    assert "slice.name = 'doFrame'" in builder.where_conditions
    assert "slice.ts >= 1000" in builder.where_conditions
    assert "slice.dur < 5000" in builder.where_conditions
    assert "slice.depth >= 1" in builder.where_conditions
    assert any("frame_id" in condition for condition in builder.where_conditions)


def test_openspec_descendants_builds_recursive_query():
    processor = _MockProcessor()
    builder = QueryBuilder(processor)

    builder.slice().id(100).descendants().name("doFrame")

    assert "WITH RECURSIVE descendant_tree" in builder.sql_parts[0]
    assert "slice.name = 'doFrame'" in builder.where_conditions


def test_openspec_series_and_position_helpers():
    processor = _MockProcessor()
    builder = QueryBuilder(processor)
    builder.slice()

    s1 = _make_slice(1, 1000, 100)
    s2 = _make_slice(2, 2000, 100)
    s3 = _make_slice(3, 3000, 100)
    builder._execute_query = lambda: [s1, s2, s3]

    assert [s.id for s in builder.series()] == [1, 2, 3]
    assert builder.first().id == 1
    assert builder.second().id == 2
    assert builder.third().id == 3
    assert builder.nth(2).id == 3
    assert builder.last().id == 3


def test_openspec_aggregate_and_to_list_support_args():
    processor = _MockProcessor()
    builder = QueryBuilder(processor)
    builder.slice()

    s1 = _make_slice(1, 1000, 10)
    s2 = _make_slice(2, 2000, 30)
    s1.get_args = types.MethodType(lambda self: {"frame_id": 100}, s1)
    s2.get_args = types.MethodType(lambda self: {"frame_id": 300}, s2)
    builder._execute_query = lambda: [s1, s2]

    assert builder.sum("dur") == 40.0
    assert builder.avg("dur") == 20.0
    assert builder.max("dur") == 30
    assert builder.min("dur") == 10
    assert builder.quantile("dur", 0.5) == 20.0
    assert builder.to_list("frame_id") == [100, 300]


def test_openspec_flow_link_query_from_slice():
    processor = Mock()
    builder = QueryBuilder(processor)
    builder.slice()

    source = _make_slice(1, 1000, 100)
    source.set_query_builder(builder)

    processor.query.side_effect = [
        [_Row(name="id"), _Row(name="slice_out"), _Row(name="slice_in"), _Row(name="name"), _Row(name="arg_set_id")],
        [
            _Row(
                id=2,
                name="target_slice",
                ts=2000,
                dur=120,
                pid=2,
                tid=2,
                cat="cat",
                track_id=2,
                depth=0,
                parent_id=None,
                arg_set_id=None,
                flow_id=11,
                flow_slice_out=1,
                flow_slice_in=2,
                flow_name="frame_render",
                flow_type=None,
                flow_category=None,
                flow_ts=None,
                flow_track_id=None,
                flow_arg_set_id=None,
            )
        ],
    ]

    links = source.flow_out().name("frame_render").series()

    assert len(links) == 1
    assert isinstance(links[0], FlowLink)
    assert links[0].slice.id == 2
    assert links[0].flow.flow_id == 11
    assert links[0].flow.name == "frame_render"
