"""
集成测试 - 测试整个DSL的工作流程
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from perfetto.dsl import Trace, Slice, Counter, Track, Flow


class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时trace文件
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False)
        self.temp_file.write(b"fake trace data")
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_basic_slice_query(self, mock_processor):
        """测试基本的slice查询"""
        # 模拟查询结果
        class MockRow:
            def __init__(self, id_val, name_val):
                self.id = id_val
                self.name = name_val
                self.ts = 1000000
                self.dur = 500000
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow(1, "test_slice")]
        mock_processor_instance = Mock()
        mock_processor_instance.query.return_value = mock_result
        mock_processor.return_value = mock_processor_instance
        
        # 测试查询
        with Trace(self.temp_file_path) as trace:
            # 测试懒加载 - 直接访问第一个结果
            first_slice = trace.slice().first()
            assert isinstance(first_slice, Slice)
            assert first_slice.id == 1
            assert first_slice.name == "test_slice"
            
            # 测试懒加载 - 使用索引访问
            slice_query = trace.slice()
            assert len(slice_query) == 1
            assert slice_query[0].id == 1
            
            # 测试懒加载 - 布尔判断
            assert bool(trace.slice()) is True
            
            # 测试懒加载 - 迭代器
            slices = list(trace.slice())
            assert len(slices) == 1
            assert isinstance(slices[0], Slice)
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_chain_query(self, mock_processor):
        """测试链式查询"""
        # 模拟查询结果
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = "test_slice"
                self.ts = 1000000
                self.dur = 500000
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow()]
        mock_processor_instance = Mock()
        mock_processor_instance.query.return_value = mock_result
        mock_processor.return_value = mock_processor_instance
        
        # 测试链式查询
        with Trace(self.temp_file_path) as trace:
            # 测试slice().process().thread()链式调用
            result = trace.slice().process(name="test_process").thread(name="test_thread")
            
            # 触发查询执行
            list(result)
            
            # 验证SQL构建
            mock_processor_instance.query.assert_called()
            call_args = mock_processor_instance.query.call_args[0][0]
            assert "SELECT slice.* FROM slice" in call_args
            assert "JOIN process_track" in call_args
            assert "JOIN process" in call_args
            assert "JOIN thread_track" in call_args
            assert "JOIN thread" in call_args
            assert "process.name = 'test_process'" in call_args
            assert "thread.name = 'test_thread'" in call_args
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_multiple_data_types(self, mock_processor):
        """测试多种数据类型查询"""
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        with Trace(self.temp_file_path) as trace:
            # 模拟counter查询结果
            class MockCounterRow:
                def __init__(self):
                    self.id = 1
                    self.name = "test_counter"
                    self.ts = 1000000
                    self.value = 42.5
                    self.pid = 123
                    self.tid = 456
                    self.cat = "test"
                    self.track_id = 789
                    self.args = None
            
            mock_processor_instance.query.return_value = [MockCounterRow()]
            
            # 测试counter查询
            counter_query = trace.counter()
            first_counter = counter_query.first()
            assert first_counter.name == "test_counter"
            assert first_counter.value == 42.5
            
            # 模拟track查询结果
            class MockTrackRow:
                def __init__(self):
                    self.id = 1
                    self.name = "test_track"
                    self.type = "slice"
                    self.pid = 123
                    self.tid = 456
                    self.cat = "test"
                    self.args = None
            
            mock_processor_instance.query.return_value = [MockTrackRow()]
            
            # 测试track查询
            track_query = trace.track()
            first_track = track_query.first()
            assert first_track.name == "test_track"
            assert first_track.type == "slice"
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_error_handling(self, mock_processor):
        """测试错误处理"""
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        with Trace(self.temp_file_path) as trace:
            # 测试查询错误
            mock_processor_instance.query.side_effect = Exception("Database error")
            
            with pytest.raises(RuntimeError, match="Failed to execute query"):
                trace.slice().first()
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_lazy_loading_caching(self, mock_processor):
        """测试懒加载缓存机制"""
        # 模拟查询结果
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = "test_slice"
                self.ts = 1000000
                self.dur = 500000
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow()]
        mock_processor_instance = Mock()
        mock_processor_instance.query.return_value = mock_result
        mock_processor.return_value = mock_processor_instance
        
        with Trace(self.temp_file_path) as trace:
            slice_query = trace.slice()
            
            # 第一次访问 - 应该执行查询
            first_slice = slice_query.first()
            assert mock_processor_instance.query.call_count == 1
            
            # 第二次访问 - 应该使用缓存，不执行新查询
            first_slice_again = slice_query.first()
            assert mock_processor_instance.query.call_count == 1  # 调用次数不变
            
            # 验证结果相同
            assert first_slice.id == first_slice_again.id
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_string_representation(self, mock_processor):
        """测试字符串表示"""
        # 模拟查询结果
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = "test_slice"
                self.ts = 1000000
                self.dur = 500000
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow()]
        mock_processor_instance = Mock()
        mock_processor_instance.query.return_value = mock_result
        mock_processor.return_value = mock_processor_instance
        
        with Trace(self.temp_file_path) as trace:
            slice_query = trace.slice()
            
            # 测试字符串表示
            str_repr = str(slice_query)
            # 由于懒加载，当只有一个结果时，会直接显示Slice对象
            assert "Slice(id=1, name='test_slice'" in str_repr
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_backward_compatibility(self, mock_processor):
        """测试向后兼容性"""
        # 模拟查询结果
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = "test_slice"
                self.ts = 1000000
                self.dur = 500000
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = 789
                self.args = None
        
        mock_result = [MockRow()]
        mock_processor_instance = Mock()
        mock_processor_instance.query.return_value = mock_result
        mock_processor.return_value = mock_processor_instance
        
        with Trace(self.temp_file_path) as trace:
            # 测试execute()方法仍然可用
            result = trace.slice().execute()
            assert isinstance(result, Slice)
            assert result.id == 1
            assert result.name == "test_slice"
