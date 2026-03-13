"""
Trace类的单元测试
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from perfetto_trace_dsl.dsl import Trace


class TestTrace:
    """Trace类测试"""
    
    def test_trace_initialization_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError, match="Trace file not found"):
            Trace("nonexistent_file.pftrace")
    
    def test_trace_initialization_invalid_extension(self):
        """测试无效文件扩展名"""
        # 创建一个临时文件来测试扩展名检查
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"fake data")
            tmp_file_path = tmp_file.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported trace format"):
                Trace(tmp_file_path)
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_trace_initialization_success(self, mock_processor):
        """测试成功初始化"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            # 模拟TraceProcessor
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            trace = Trace(tmp_file_path)
            
            assert trace.file == tmp_file_path
            assert trace.trace_processor == mock_processor_instance
            mock_processor.assert_called_once_with(trace=tmp_file_path)
            
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_trace_processor_property(self, mock_processor):
        """测试trace_processor属性"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            trace = Trace(tmp_file_path)
            
            # 测试正常获取
            assert trace.trace_processor == mock_processor_instance
            
            # 测试trace_processor属性
            assert trace.trace_processor == mock_processor_instance
                
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_context_manager(self, mock_processor):
        """测试上下文管理器"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            with Trace(tmp_file_path) as trace:
                assert trace.trace_processor == mock_processor_instance
            
            # 验证close被调用
            mock_processor_instance.close.assert_called_once()
            
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_slice_method(self, mock_processor):
        """测试slice方法"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            trace = Trace(tmp_file_path)
            
            # 测试不带参数的slice调用
            result = trace.slice()
            assert hasattr(result, 'slice')  # 返回QueryBuilder
            
            # 测试带参数的slice调用
            result = trace.slice(id=1, name="test")
            assert hasattr(result, 'slice')  # 返回QueryBuilder
            
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_counter_method(self, mock_processor):
        """测试counter方法"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            trace = Trace(tmp_file_path)
            
            result = trace.counter(name="test_counter")
            assert hasattr(result, 'counter')  # 返回QueryBuilder
            
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_track_method(self, mock_processor):
        """测试track方法"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            trace = Trace(tmp_file_path)
            
            result = trace.track(type="slice")
            assert hasattr(result, 'track')  # 返回QueryBuilder
            
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_flow_method(self, mock_processor):
        """测试flow方法"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            trace = Trace(tmp_file_path)
            
            result = trace.flow(source_slice_id=1)
            assert hasattr(result, 'flow')  # 返回QueryBuilder
            
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_query_method(self, mock_processor):
        """测试query方法"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            # 模拟查询结果
            mock_result = [
                {'id': 1, 'name': 'test1'},
                {'id': 2, 'name': 'test2'}
            ]
            mock_processor_instance.query.return_value = mock_result
            
            trace = Trace(tmp_file_path)
            
            # 测试查询
            results = list(trace.query("SELECT * FROM slice"))
            assert len(results) == 2
            assert results[0] == {'id': 1, 'name': 'test1'}
            assert results[1] == {'id': 2, 'name': 'test2'}
            
            mock_processor_instance.query.assert_called_once_with("SELECT * FROM slice")
            
        finally:
            os.unlink(tmp_file_path)
    
    @patch('perfetto_trace_dsl.dsl.trace.TraceProcessor')
    def test_query_method_error(self, mock_processor):
        """测试query方法的错误处理"""
        with tempfile.NamedTemporaryFile(suffix='.pftrace', delete=False) as tmp_file:
            tmp_file.write(b"fake trace data")
            tmp_file_path = tmp_file.name
        
        try:
            mock_processor_instance = Mock()
            mock_processor.return_value = mock_processor_instance
            
            # 模拟查询错误
            mock_processor_instance.query.side_effect = Exception("Query failed")
            
            trace = Trace(tmp_file_path)
            
            with pytest.raises(RuntimeError, match="Failed to execute query"):
                list(trace.query("SELECT * FROM slice"))
            
        finally:
            os.unlink(tmp_file_path)
