import pytest
from perfetto.dsl import Trace, Slice, Counter, Track, Flow
from perfetto.dsl.query_builder import QueryBuilder
from perfetto.dsl.related_objects import RelatedObjectsAccessor


class TestBasicFunctionality:
    """基本功能测试"""
    
    def test_slice_creation(self):
        """测试 Slice 对象创建"""
        slice_data = {
            'id': 1,
            'name': 'test_slice',
            'ts': 1000000,
            'dur': 500000,
            'pid': 1234,
            'tid': 5678,
            'cat': 'test_category',
            'track_id': 1,
            'depth': 0,
            'parent_id': None,
            'arg_set_id': 4001
        }
        
        slice_obj = Slice.from_dict(slice_data)
        
        assert slice_obj.id == 1
        assert slice_obj.name == 'test_slice'
        assert slice_obj.start_time_ns == 1000000
        assert slice_obj.duration_ns == 500000
        assert slice_obj.start_time_ms == 1.0
        assert slice_obj.duration_ms == 0.5
        # get_arg 需要 QueryBuilder 才能工作，这里只测试基本功能
        assert slice_obj.get_arg('key') is None
    
    def test_slice_input_id_extraction(self):
        """测试 input_id 提取"""
        slice_obj = Slice(
            id=1, name="Some operation id=0x1dc76a4d", ts=0, dur=0,
            pid=0, tid=0, cat="", track_id=0
        )
        
        input_id = slice_obj.input_id()
        assert input_id == "0x1dc76a4d"
    
    def test_slice_frame_id_extraction(self):
        """测试 frame_id 提取"""
        slice_obj = Slice(
            id=1, name="Choreographer#doFrame 787448", ts=0, dur=0,
            pid=0, tid=0, cat="", track_id=0
        )
        
        frame_id = slice_obj.frame_id()
        assert frame_id == 787448
    
    def test_counter_creation(self):
        """测试 Counter 对象创建"""
        counter_data = {
            'id': 1,
            'name': 'test_counter',
            'ts': 1000000,
            'value': 42.5,
            'track_id': 1
        }
        
        counter_obj = Counter.from_dict(counter_data)
        
        assert counter_obj.id == 1
        assert counter_obj.name == 'test_counter'
        assert counter_obj.timestamp_ns == 1000000
        assert counter_obj.timestamp_ms == 1.0
        assert counter_obj.value == 42.5
    
    def test_track_creation(self):
        """测试 Track 对象创建"""
        track_data = {
            'id': 1,
            'name': 'test_track',
            'type': 'slice_track',
            'pid': 1234,
            'tid': 5678,
            'cat': 'test_category',
            'args': {'key': 'value'}
        }
        
        track_obj = Track.from_dict(track_data)
        
        assert track_obj.id == 1
        assert track_obj.name == 'test_track'
        assert track_obj.type == 'slice_track'
        assert track_obj.pid == 1234
        assert track_obj.tid == 5678
        assert track_obj.get_arg('key') == 'value'
    
    def test_flow_creation(self):
        """测试 Flow 对象创建"""
        flow_data = {
            'id': 1,
            'slice_out': 100,
            'slice_in': 200,
            'name': 'test_flow',
            'args': {'key': 'value'}
        }
        
        flow_obj = Flow.from_dict(flow_data)
        
        assert flow_obj.id == 1
        assert flow_obj.slice_out == 100
        assert flow_obj.slice_in == 200
        assert flow_obj.name == 'test_flow'
        assert flow_obj.get_arg('key') == 'value'
    
    def test_enhanced_slice_creation(self):
        """测试 Slice 对象创建"""
        slice_data = {
            'id': 1,
            'name': 'test_slice',
            'ts': 1000000,
            'dur': 500000,
            'pid': 1234,
            'tid': 5678,
            'cat': 'test_category',
            'track_id': 1,
            'depth': 0,
            'parent_id': None,
            'arg_set_id': 4001
        }
        
        enhanced_slice = Slice.from_dict(slice_data)
        
        assert enhanced_slice.id == 1
        assert enhanced_slice.name == 'test_slice'
        assert enhanced_slice._query_builder is None
        assert enhanced_slice._related_objects is None
    
    def test_query_builder_initialization(self):
        """测试 QueryBuilder 初始化"""
        # 模拟 trace_processor
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        assert builder.trace_processor == mock_processor
        assert builder.current_table is None
        assert builder.result_type is None
        assert builder.sql_parts == []
        assert builder.joins == []
        assert builder.where_conditions == []
        assert builder._executed is False
        assert builder._results is None
    
    def test_slice_query_builder(self):
        """测试 slice 查询构建器"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试基本的 slice 查询
        result = builder.slice(name="test")
        
        assert result == builder  # 返回自身以支持链式调用
        assert builder.current_table == "slice"
        assert builder.result_type == Slice
        assert "slice.name LIKE '%test%'" in builder.where_conditions
    
    def test_slice_query_with_wildcard(self):
        """测试带通配符的 slice 查询"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试通配符查询
        result = builder.slice(name="%test%")
        
        assert "slice.name LIKE '%test%'" in builder.where_conditions
    
    def test_process_query_builder(self):
        """测试 process 查询构建器"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 然后添加 process 查询
        result = builder.process(name="test_process")
        
        assert result == builder
        assert "JOIN process_track ON slice.track_id = process_track.id" in builder.joins
        assert "JOIN process ON process_track.upid = process.upid" in builder.joins
        assert "process.name LIKE 'test_process'" in builder.where_conditions
    
    def test_thread_query_builder(self):
        """测试 thread 查询构建器"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 然后添加 thread 查询
        result = builder.thread(name="test_thread")
        
        assert result == builder
        assert "JOIN thread_track ON slice.track_id = thread_track.id" in builder.joins
        assert "JOIN thread ON thread_track.utid = thread.utid" in builder.joins
        assert "thread.name LIKE 'test_thread'" in builder.where_conditions
    
    def test_main_thread_query(self):
        """测试主线程查询"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 然后添加主线程查询
        result = builder.thread(main=True)
        
        assert result == builder
        assert "thread.is_main_thread = 1" in builder.where_conditions
    
    def test_flow_out_query_builder(self):
        """测试 flow_out 查询构建器"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 然后添加 flow_out 查询
        result = builder.flow_out()
        
        assert result == builder
        assert builder.current_table == "slice_out"
        assert "JOIN flow ON slice.id = flow.slice_out" in builder.joins
        assert "JOIN slice slice_out ON flow.slice_in = slice_out.id" in builder.joins
    
    def test_flow_in_query_builder(self):
        """测试 flow_in 查询构建器"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 然后添加 flow_in 查询
        result = builder.flow_in()
        
        assert result == builder
        assert builder.current_table == "slice_in"
        assert "JOIN flow ON slice.id = flow.slice_in" in builder.joins
        assert "JOIN slice slice_in ON flow.slice_out = slice_in.id" in builder.joins
    
    def test_time_boundary_queries(self):
        """测试时间界定符查询"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 创建测试 slice
        test_slice = Slice(
            id=1, name="test", ts=1000000, dur=500000,
            pid=0, tid=0, cat="", track_id=0
        )
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试 after 查询
        result = builder.after(test_slice)
        assert "slice.ts > 1500000" in builder.where_conditions  # 1000000 + 500000
        
        # 重置条件
        builder.where_conditions = []
        
        # 测试 before 查询
        result = builder.before(test_slice)
        assert "slice.ts < 1000000" in builder.where_conditions
        
        # 重置条件
        builder.where_conditions = []
        
        # 测试 between 查询（单个参数）
        result = builder.between(test_slice)
        # between方法现在需要两个参数，单个参数会创建时间范围条件
        assert "slice.ts < 1500000" in " ".join(builder.where_conditions)
        assert "slice.ts + slice.dur > 1000000" in " ".join(builder.where_conditions)
    
    def test_limit_and_order_by(self):
        """测试 limit 和 order_by"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试 limit
        result = builder.limit(10)
        assert result == builder
        assert builder.limit_count == 10
        
        # 测试 order_by
        result = builder.order_by("slice.ts DESC")
        assert result == builder
        assert builder.order_by_clause == "slice.ts DESC"
    
    
    def test_before_with_string_parameter(self):
        """测试 before 方法支持字符串参数"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试 before 方法传入字符串
        result = builder.before("test_slice")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts <" in condition for condition in builder.where_conditions)
    
    def test_after_with_string_parameter(self):
        """测试 after 方法支持字符串参数"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试 after 方法传入字符串
        result = builder.after("test_slice")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts >" in condition for condition in builder.where_conditions)
    
    def test_between_with_string_parameters(self):
        """测试 between 方法支持字符串参数"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试 between 方法传入字符串
        result = builder.between("start_slice", "end_slice")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts <" in condition for condition in builder.where_conditions)
        assert any("slice.ts + slice.dur >" in condition for condition in builder.where_conditions)
    
    def test_between_with_single_string_parameter(self):
        """测试 between 方法支持单个字符串参数"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试 between 方法传入单个字符串
        result = builder.between("test_slice")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts <" in condition for condition in builder.where_conditions)
        assert any("slice.ts + slice.dur >" in condition for condition in builder.where_conditions)
    
    def test_parse_slice_spec_simple(self):
        """测试解析简单slice规格"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试简单名称
        result = builder._parse_slice_spec("playing")
        assert result['name'] == "playing"
        assert result['process'] is None
        assert result['thread'] is None
        assert result['track'] is None
        assert result['index'] is None
    
    def test_parse_slice_spec_with_process(self):
        """测试解析带进程名的slice规格"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试带进程名
        result = builder._parse_slice_spec("playing|com.example.app")
        assert result['name'] == "playing"
        assert result['process'] == "com.example.app"
        assert result['thread'] is None
        assert result['track'] is None
        assert result['index'] is None
    
    def test_parse_slice_spec_with_thread(self):
        """测试解析带线程名的slice规格"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试带进程名和线程名
        result = builder._parse_slice_spec("playing|com.example.app||main")
        assert result['name'] == "playing"
        assert result['process'] == "com.example.app"
        assert result['thread'] == "main"
        assert result['track'] is None
        assert result['index'] is None
    
    def test_parse_slice_spec_with_track(self):
        """测试解析带Track名的slice规格"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试带进程名、线程名和Track名
        result = builder._parse_slice_spec("playing|com.example.app||main|||track_name")
        assert result['name'] == "playing"
        assert result['process'] == "com.example.app"
        assert result['thread'] == "main"
        assert result['track'] == "track_name"
        assert result['index'] is None
    
    def test_parse_slice_spec_with_index(self):
        """测试解析带索引的slice规格"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试带索引
        result = builder._parse_slice_spec("playing|com.example.app||main|||track_name#1")
        assert result['name'] == "playing"
        assert result['process'] == "com.example.app"
        assert result['thread'] == "main"
        assert result['track'] == "track_name"
        assert result['index'] == 1
        
        # 测试最后一个索引
        result = builder._parse_slice_spec("playing|com.example.app||main|||track_name#-1")
        assert result['index'] == -1
    
    def test_parse_slice_spec_partial_specs(self):
        """测试解析部分规格的slice"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试只有进程名和索引
        result = builder._parse_slice_spec("playing|com.example.app#0")
        assert result['name'] == "playing"
        assert result['process'] == "com.example.app"
        assert result['thread'] is None
        assert result['track'] is None
        assert result['index'] == 0
        
        # 测试只有进程名和线程名，带索引
        result = builder._parse_slice_spec("playing|com.example.app||main#2")
        assert result['name'] == "playing"
        assert result['process'] == "com.example.app"
        assert result['thread'] == "main"
        assert result['track'] is None
        assert result['index'] == 2
    
    def test_before_with_advanced_syntax(self):
        """测试 before 方法支持高级语法"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试高级语法
        result = builder.before("playing@com.example.app@@main@@@track_name#1")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts <" in condition for condition in builder.where_conditions)
    
    def test_after_with_advanced_syntax(self):
        """测试 after 方法支持高级语法"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试高级语法
        result = builder.after("playing@com.example.app@@main@@@track_name#-1")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts >" in condition for condition in builder.where_conditions)
    
    def test_between_with_advanced_syntax(self):
        """测试 between 方法支持高级语法"""
        class MockTraceProcessor:
            def query(self, sql):
                return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 先设置 slice 查询
        builder.slice()
        
        # 测试高级语法
        result = builder.between("start@com.example.app@@main@@@track_name#0", "end@com.example.app@@main@@@track_name#-1")
        
        assert result == builder
        # 验证生成了正确的条件
        assert any("slice.ts <" in condition for condition in builder.where_conditions)
        assert any("slice.ts + slice.dur >" in condition for condition in builder.where_conditions)
    
    def test_multiple_slices_error_handling(self):
        """测试多slice匹配时的错误处理"""
        class MockTraceProcessor:
            def query(self, sql):
                # 模拟返回多个slice的情况
                if "COUNT(*)" in sql:
                    # 返回计数查询结果
                    class MockCountResult:
                        def __init__(self):
                            self.slice_count = 3
                    return [MockCountResult()]
                else:
                    # 返回slice查询结果
                    class MockSlice:
                        def __init__(self, id, name, ts):
                            self.id = id
                            self.name = name
                            self.ts = ts
                            self.dur = 1000000
                            self.pid = 1234
                            self.tid = 5678
                            self.cat = "test"
                            self.track_id = 1
                            self.depth = 0
                            self.parent_id = None
                            self.arg_set_id = None
                        
                        def __str__(self):
                            return f"Slice(id={self.id}, name='{self.name}', ts={self.ts}ms)"
                    
                    return [
                        MockSlice(1, "playing", 1000000),
                        MockSlice(2, "playing", 2000000),
                        MockSlice(3, "playing", 3000000)
                    ]
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试多slice匹配时的错误
        try:
            builder._create_slice_query_from_name("playing@com.example.app")
            assert False, "应该抛出ValueError"
        except ValueError as e:
            error_msg = str(e)
            assert "匹配到 3 个slice" in error_msg
            assert "请指定索引" in error_msg
            assert "playing@com.example.app#0" in error_msg
            assert "playing@com.example.app#1" in error_msg
            assert "playing@com.example.app#-1" in error_msg
    
    def test_single_slice_no_error(self):
        """测试单个slice匹配时不报错"""
        class MockTraceProcessor:
            def query(self, sql):
                # 模拟返回单个slice的情况
                if "COUNT(*)" in sql:
                    class MockCountResult:
                        def __init__(self):
                            self.slice_count = 1
                    return [MockCountResult()]
                else:
                    class MockSlice:
                        def __init__(self):
                            self.id = 1
                            self.name = "playing"
                            self.ts = 1000000
                            self.dur = 1000000
                            self.pid = 1234
                            self.tid = 5678
                            self.cat = "test"
                            self.track_id = 1
                            self.depth = 0
                            self.parent_id = None
                            self.arg_set_id = None
                    
                    return [MockSlice()]
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试单个slice匹配时不报错
        try:
            result = builder._create_slice_query_from_name("playing@com.example.app")
            assert result is not None
            assert result.current_table == "slice"
            assert result.limit_count == 1
        except ValueError:
            assert False, "单个slice匹配时不应该报错"
    
    def test_no_slice_found(self):
        """测试没有找到slice的情况"""
        class MockTraceProcessor:
            def query(self, sql):
                # 模拟没有找到slice的情况
                if "COUNT(*)" in sql:
                    class MockCountResult:
                        def __init__(self):
                            self.slice_count = 0
                    return [MockCountResult()]
                else:
                    return []
        
        mock_processor = MockTraceProcessor()
        builder = QueryBuilder(mock_processor)
        
        # 测试没有找到slice的情况
        try:
            result = builder._create_slice_query_from_name("nonexistent@com.example.app")
            assert result is not None
            assert "1 = 0" in result.where_conditions  # 应该添加永远不匹配的条件
        except ValueError:
            assert False, "没有找到slice时不应该报错"