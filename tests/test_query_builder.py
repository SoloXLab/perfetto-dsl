"""
QueryBuilder类的单元测试
"""

import pytest
from unittest.mock import Mock
from perfetto.dsl import QueryBuilder, Slice, Counter, Track, Flow


class TestQueryBuilder:
    """QueryBuilder类测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_processor = Mock()
        self.builder = QueryBuilder(self.mock_processor)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.builder.trace_processor == self.mock_processor
        assert self.builder.sql_parts == []
        assert self.builder.joins == []
        assert self.builder.where_conditions == []
        assert self.builder.current_table is None
        assert self.builder.result_type is None
        assert self.builder._results is None
        assert self.builder._executed is False
    
    def test_slice_method(self):
        """测试slice方法"""
        result = self.builder.slice(id=1, name="test")
        
        assert result is self.builder  # 返回自身以支持链式调用
        assert self.builder.current_table == "slice"
        assert self.builder.result_type == Slice
        assert "SELECT slice.* FROM slice" in self.builder.sql_parts[0]
        assert "slice.id = 1" in self.builder.where_conditions
        assert "slice.name LIKE '%test%'" in self.builder.where_conditions
    
    def test_slice_method_with_duration_filters(self):
        """测试slice方法的时间过滤"""
        self.builder.slice().filter("duration>=1.0").filter("duration<=5.0")
        
        assert "slice.dur >= 1000000" in self.builder.where_conditions  # 1.0ms = 1000000ns
        assert "slice.dur <= 5000000" in self.builder.where_conditions  # 5.0ms = 5000000ns
    
    def test_filter_method(self):
        """测试filter方法"""
        # 测试duration过滤
        self.builder.slice().filter("duration>1.0")
        assert "slice.dur > 1000000" in self.builder.where_conditions
        
        # 测试其他字段过滤
        self.builder.slice().filter("id>1000")
        assert "slice.id > 1000" in self.builder.where_conditions
        
        # 测试字符串过滤
        self.builder.slice().filter("name='test_slice'")
        assert "slice.name = 'test_slice'" in self.builder.where_conditions
        
        # 测试多个过滤条件
        self.builder.slice().filter("duration>=1.0").filter("duration<=10.0")
        assert "slice.dur >= 1000000" in self.builder.where_conditions
        assert "slice.dur <= 10000000" in self.builder.where_conditions
    
    def test_before_method(self):
        """测试before方法"""
        # 创建边界查询
        boundary_query = QueryBuilder(self.mock_processor)
        boundary_query.slice(id=123)
        
        # 测试before
        self.builder.slice().before(boundary_query)
        assert "slice.ts < (SELECT ts FROM (SELECT slice.* FROM slice WHERE slice.id = 123) LIMIT 1)" in self.builder.where_conditions
    
    def test_after_method(self):
        """测试after方法"""
        # 创建边界查询
        boundary_query = QueryBuilder(self.mock_processor)
        boundary_query.slice(id=123)
        
        # 测试after
        self.builder.slice().after(boundary_query)
        assert "slice.ts > (SELECT ts + dur FROM (SELECT slice.* FROM slice WHERE slice.id = 123) LIMIT 1)" in self.builder.where_conditions
    
    def test_between_method(self):
        """测试between方法"""
        # 创建边界查询
        boundary_query = QueryBuilder(self.mock_processor)
        boundary_query.slice(id=123)
        
        # 测试between（单个slice）
        self.builder.slice().between(boundary_query)
        # between条件包含换行符，所以我们需要检查部分匹配
        between_condition_part1 = "slice.ts < (SELECT ts + dur FROM (SELECT slice.* FROM slice WHERE slice.id = 123) LIMIT 1)"
        between_condition_part2 = "slice.ts + slice.dur > (SELECT ts FROM (SELECT slice.* FROM slice WHERE slice.id = 123) LIMIT 1)"
        
        # 检查between条件是否包含这两个部分
        between_conditions = [cond for cond in self.builder.where_conditions if "AND" in cond]
        assert len(between_conditions) > 0
        between_condition_str = between_conditions[0]
        assert between_condition_part1 in between_condition_str
        assert between_condition_part2 in between_condition_str
    
    def test_process_method(self):
        """测试process方法"""
        # 先调用slice
        self.builder.slice()
        
        # 再调用process
        result = self.builder.process(name="test_process", pid=123)
        
        assert result is self.builder
        assert "JOIN process_track ON slice.track_id = process_track.id" in self.builder.joins
        assert "JOIN process ON process_track.upid = process.upid" in self.builder.joins
        assert "process.name LIKE 'test_process'" in self.builder.where_conditions
        assert "process.pid = 123" in self.builder.where_conditions
    
    def test_process_method_without_slice(self):
        """测试在没有slice的情况下调用process"""
        with pytest.raises(ValueError, match="process\\(\\) can only be called after slice\\(\\)"):
            self.builder.process(name="test")
    
    def test_thread_method(self):
        """测试thread方法"""
        # 先调用slice
        self.builder.slice()
        
        # 再调用thread
        result = self.builder.thread(name="test_thread", tid=456)
        
        assert result is self.builder
        assert "JOIN thread_track ON slice.track_id = thread_track.id" in self.builder.joins
        assert "JOIN thread ON thread_track.utid = thread.utid" in self.builder.joins
        assert "thread.name LIKE 'test_thread'" in self.builder.where_conditions
        assert "thread.tid = 456" in self.builder.where_conditions
    
    def test_thread_method_without_slice(self):
        """测试在没有slice的情况下调用thread"""
        with pytest.raises(ValueError, match="thread\\(\\) can only be called after slice\\(\\)"):
            self.builder.thread(name="test")
    
    def test_counter_method(self):
        """测试counter方法"""
        result = self.builder.counter(name="test_counter", track_id=789)
        
        assert result is self.builder
        assert self.builder.current_table == "counter"
        assert self.builder.result_type == Counter
        assert "SELECT" in self.builder.sql_parts[0] and "counter.*" in self.builder.sql_parts[0]
        assert "counter_track.name = 'test_counter'" in self.builder.where_conditions
        assert "counter.track_id = 789" in self.builder.where_conditions
    
    def test_track_method(self):
        """测试track方法"""
        result = self.builder.track(name="test_track", type="slice")
        
        assert result is self.builder
        assert self.builder.current_table == "track"
        assert self.builder.result_type == Track
        assert "SELECT track.* FROM track" in self.builder.sql_parts[0]
        assert "track.name LIKE 'test_track'" in self.builder.where_conditions
        assert "track.type LIKE 'slice'" in self.builder.where_conditions
    
    def test_flow_method(self):
        """测试flow方法"""
        result = self.builder.flow(source_slice_id=1, target_slice_id=2)
        
        assert result is self.builder
        assert self.builder.current_table == "flow"
        assert self.builder.result_type == Flow
        assert "SELECT flow.* FROM flow" in self.builder.sql_parts[0]
        assert "flow.source_slice_id = 1" in self.builder.where_conditions
        assert "flow.target_slice_id = 2" in self.builder.where_conditions
    
    def test_execute_without_query(self):
        """测试在没有查询的情况下执行"""
        with pytest.raises(ValueError, match="No query specified"):
            self.builder.execute()
    
    def test_execute_slice_query(self):
        """测试执行slice查询"""
        # 设置查询
        self.builder.slice(id=1)
        
        # 模拟查询结果
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = "test_slice"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow()]
        self.mock_processor.query.return_value = mock_result
        
        # 执行查询
        result = self.builder.execute()
        
        # 验证结果
        assert isinstance(result, Slice)
        assert result.id == 1
        assert result.name == "test_slice"
        assert self.builder._executed is True
        assert self.builder._results is not None
    
    def test_execute_multiple_results(self):
        """测试执行返回多个结果的查询"""
        # 设置查询
        self.builder.slice()
        
        # 模拟多个查询结果
        class MockRow:
            def __init__(self, id_val, name_val):
                self.id = id_val
                self.name = name_val
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1, "slice1"), MockRow(2, "slice2")]
        self.mock_processor.query.return_value = mock_result
        
        # 执行查询
        result = self.builder.execute()
        
        # 验证结果
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], Slice)
        assert result[0].id == 1
        assert result[0].name == "slice1"
        assert result[1].id == 2
        assert result[1].name == "slice2"
    
    def test_execute_no_results(self):
        """测试执行没有结果的查询"""
        # 设置查询
        self.builder.slice(id=999)
        
        # 模拟空结果
        self.mock_processor.query.return_value = []
        
        # 执行查询
        result = self.builder.execute()
        
        # 验证结果
        assert result is None
    
    def test_execute_error(self):
        """测试执行查询时的错误处理"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询错误
        self.mock_processor.query.side_effect = Exception("Database error")
        
        # 执行查询
        with pytest.raises(RuntimeError, match="Failed to execute query"):
            self.builder.execute()
    
    def test_iter_method(self):
        """测试迭代器方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试迭代
        results = list(self.builder)
        assert len(results) == 2
        assert isinstance(results[0], Slice)
        assert results[0].id == 1
        assert results[1].id == 2
    
    def test_getitem_method(self):
        """测试索引访问方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试索引访问
        assert isinstance(self.builder[0], Slice)
        assert self.builder[0].id == 1
        assert self.builder[1].id == 2
    
    def test_len_method(self):
        """测试长度方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2), MockRow(3)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试长度
        assert len(self.builder) == 3
    
    def test_bool_method(self):
        """测试布尔判断方法"""
        # 设置查询
        self.builder.slice()
        
        # 测试有结果的情况
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = "test"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        self.mock_processor.query.return_value = [MockRow()]
        assert bool(self.builder) is True
        
        # 测试无结果的情况
        self.builder._executed = False  # 重置状态
        self.mock_processor.query.return_value = []
        assert bool(self.builder) is False
    
    def test_first_method(self):
        """测试first方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试first方法
        first = self.builder.first()
        assert isinstance(first, Slice)
        assert first.id == 1
        
        # 测试无结果的情况
        self.builder._executed = False  # 重置状态
        self.mock_processor.query.return_value = []
        assert self.builder.first() is None
    
    def test_last_method(self):
        """测试last方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试last方法
        last = self.builder.last()
        assert isinstance(last, Slice)
        assert last.id == 2
        
        # 测试无结果的情况
        self.builder._executed = False  # 重置状态
        self.mock_processor.query.return_value = []
        assert self.builder.last() is None
    
    def test_count_method(self):
        """测试count方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2), MockRow(3)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试count方法
        # count方法会直接执行SQL查询，所以需要mock SQL查询结果
        class MockCountRow:
            def __init__(self):
                self.slice_count = 3
        
        self.mock_processor.query.return_value = [MockCountRow()]
        assert self.builder.count() == 3
    
    def test_all_method(self):
        """测试all方法"""
        # 设置查询
        self.builder.slice()
        
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val):
                self.id = id_val
                self.name = f"slice{id_val}"
                self.ts = 1000
                self.dur = 500
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1), MockRow(2)]
        self.mock_processor.query.return_value = mock_result
        
        # 测试all方法
        all_results = self.builder.all()
        assert isinstance(all_results, list)
        assert len(all_results) == 2
        assert all(isinstance(r, Slice) for r in all_results)
