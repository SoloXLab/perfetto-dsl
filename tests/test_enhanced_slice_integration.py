"""
增强Slice功能的集成测试
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from perfetto.dsl import Trace


class TestEnhancedSliceIntegration:
    """增强Slice功能的集成测试"""
    
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
    def test_slice_process_name_access(self, mock_processor):
        """测试slice.process.name访问"""
        # 模拟slice查询结果
        class MockSliceRow:
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
        
        # 模拟process查询结果
        class MockProcessRow:
            def __init__(self):
                self.name = "test_process"
                self.pid = 123
                self.upid = 456
        
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        # 设置查询结果
        def mock_query(sql):
            if "SELECT slice.* FROM slice" in sql:
                return [MockSliceRow()]
            elif "SELECT process.*" in sql and "process_track" in sql:
                return [MockProcessRow()]
            else:
                return []
        
        mock_processor_instance.query.side_effect = mock_query
        
        # 测试功能
        with Trace(self.temp_file_path) as trace:
            slice_obj = trace.slice().first()
            
            # 测试直接访问process.name
            process_name = slice_obj.process.name
            assert process_name == "test_process"
            
            # 测试访问其他process属性
            assert slice_obj.process.pid == 123
            assert slice_obj.process.upid == 456
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_slice_thread_name_access(self, mock_processor):
        """测试slice.thread.name访问"""
        # 模拟slice查询结果
        class MockSliceRow:
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
        
        # 模拟thread查询结果
        class MockThreadRow:
            def __init__(self):
                self.name = "test_thread"
                self.tid = 456
                self.utid = 789
        
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        # 设置查询结果
        def mock_query(sql):
            if "SELECT slice.* FROM slice" in sql:
                return [MockSliceRow()]
            elif "SELECT thread.*" in sql and "thread_track" in sql:
                return [MockThreadRow()]
            else:
                return []
        
        mock_processor_instance.query.side_effect = mock_query
        
        # 测试功能
        with Trace(self.temp_file_path) as trace:
            slice_obj = trace.slice().first()
            
            # 测试直接访问thread.name
            thread_name = slice_obj.thread.name
            assert thread_name == "test_thread"
            
            # 测试访问其他thread属性
            assert slice_obj.thread.tid == 456
            assert slice_obj.thread.utid == 789
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_slice_track_access(self, mock_processor):
        """测试slice.track访问"""
        # 模拟slice查询结果
        class MockSliceRow:
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
        
        # 模拟track查询结果
        class MockTrackRow:
            def __init__(self):
                self.id = 789
                self.name = "test_track"
                self.type = "slice"
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.args = None
        
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        # 设置查询结果
        def mock_query(sql):
            if "SELECT slice.* FROM slice" in sql:
                return [MockSliceRow()]
            else:
                return []
        
        mock_processor_instance.query.side_effect = mock_query
        
        # 模拟track查询的链式调用
        mock_track = Mock()
        mock_track.id = 789
        mock_track.name = "test_track"
        mock_track.type = "slice"
        mock_track.pid = 123
        mock_track.tid = 456
        mock_track.cat = "test"
        mock_track.args = None
        
        # 我们需要patch QueryBuilder的track方法
        with patch('perfetto.dsl.query_builder.QueryBuilder.track') as mock_track_method:
            mock_track_query = Mock()
            mock_track_query.first.return_value = mock_track
            mock_track_method.return_value = mock_track_query
        
            # 测试功能
            with Trace(self.temp_file_path) as trace:
                slice_obj = trace.slice().first()
                
                # 测试直接访问track
                track = slice_obj.track
                assert track is not None
                assert track.name == "test_track"
                assert track.type == "slice"
                assert track.id == 789
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_chain_access_pattern(self, mock_processor):
        """测试链式访问模式"""
        # 模拟slice查询结果
        class MockSliceRow:
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
        
        # 模拟process查询结果
        class MockProcessRow:
            def __init__(self):
                self.name = "my_app"
                self.pid = 123
                self.upid = 456
        
        # 模拟thread查询结果
        class MockThreadRow:
            def __init__(self):
                self.name = "main_thread"
                self.tid = 456
                self.utid = 789
        
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        # 设置查询结果
        def mock_query(sql):
            if "SELECT slice.* FROM slice" in sql:
                return [MockSliceRow()]
            elif "SELECT process.*" in sql and "process_track" in sql:
                return [MockProcessRow()]
            elif "SELECT thread.*" in sql and "thread_track" in sql:
                return [MockThreadRow()]
            else:
                return []
        
        mock_processor_instance.query.side_effect = mock_query
        
        # 测试功能
        with Trace(self.temp_file_path) as trace:
            slice_obj = trace.slice().first()
            
            # 测试链式访问
            process_name = slice_obj.process.name
            thread_name = slice_obj.thread.name
            track_name = slice_obj.track.name if slice_obj.track else None
            
            assert process_name == "my_app"
            assert thread_name == "main_thread"
            # track查询可能失败，这里不强制要求
    
    @patch('perfetto.dsl.trace.TraceProcessor')
    def test_multiple_slices_with_related_objects(self, mock_processor):
        """测试多个slice的关联对象访问"""
        # 模拟多个slice查询结果
        class MockSliceRow:
            def __init__(self, id_val, track_id_val):
                self.id = id_val
                self.name = f"slice_{id_val}"
                self.ts = 1000000
                self.dur = 500000
                self.pid = 123
                self.tid = 456
                self.cat = "test"
                self.track_id = track_id_val
                self.args = None
        
        # 模拟process查询结果
        class MockProcessRow:
            def __init__(self, name_val):
                self.name = name_val
                self.pid = 123
                self.upid = 456
        
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        
        # 设置查询结果
        def mock_query(sql):
            if "SELECT slice.* FROM slice" in sql:
                return [MockSliceRow(1, 789), MockSliceRow(2, 790)]
            elif "SELECT process.*" in sql and "process_track" in sql:
                return [MockProcessRow("app_process")]
            else:
                return []
        
        mock_processor_instance.query.side_effect = mock_query
        
        # 测试功能
        with Trace(self.temp_file_path) as trace:
            slices = list(trace.slice())
            
            assert len(slices) == 2
            
            # 测试每个slice的关联对象访问
            for i, slice_obj in enumerate(slices):
                assert slice_obj.id == i + 1
                assert slice_obj.name == f"slice_{i + 1}"
                
                # 测试process访问
                process_name = slice_obj.process.name
                assert process_name == "app_process"
