"""
测试关联对象访问功能
"""

import pytest
from unittest.mock import Mock, patch
from perfetto.dsl import Slice
from perfetto.dsl.related_objects import RelatedObjectsAccessor


class TestRelatedObjectsAccessor:
    """测试关联对象访问器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_query_builder = Mock()
        self.mock_slice = Mock()
        self.mock_slice.track_id = 123
        self.accessor = RelatedObjectsAccessor(self.mock_query_builder, self.mock_slice)
    
    def test_track_property(self):
        """测试track属性访问"""
        # 创建mock的track对象
        mock_track = Mock()
        mock_track.id = 123
        mock_track.name = "test_track"
        mock_track.type = "slice"
        mock_track.pid = 456
        mock_track.tid = 789
        mock_track.cat = "test"
        mock_track.args = None
        
        # 设置mock的链式调用
        mock_track_query = Mock()
        mock_track_query.first.return_value = mock_track
        self.mock_query_builder.track.return_value = mock_track_query
        
        # 测试track属性
        track = self.accessor.track
        assert track is not None
        assert track.id == 123
        assert track.name == "test_track"
        assert track.type == "slice"
        
        # 验证track查询被调用
        self.mock_query_builder.track.assert_called_with(id=123)
    
    def test_track_property_no_result(self):
        """测试track属性无结果的情况"""
        # 设置mock的链式调用返回None
        mock_track_query = Mock()
        mock_track_query.first.return_value = None
        self.mock_query_builder.track.return_value = mock_track_query
        
        track = self.accessor.track
        assert track is None
    
    def test_process_property(self):
        """测试process属性访问"""
        process_accessor = self.accessor.process
        assert isinstance(process_accessor, ProcessAccessor)
    
    def test_thread_property(self):
        """测试thread属性访问"""
        thread_accessor = self.accessor.thread
        assert isinstance(thread_accessor, ThreadAccessor)


class TestProcessAccessor:
    """测试Process访问器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_query_builder = Mock()
        self.mock_slice = Mock()
        self.mock_slice.track_id = 123
        self.accessor = ProcessAccessor(self.mock_query_builder, self.mock_slice)
    
    def test_process_attribute_access(self):
        """测试process属性访问"""
        # 模拟process查询结果
        class MockProcessRow:
            def __init__(self):
                self.name = "test_process"
                self.pid = 456
                self.upid = 789
        
        mock_result = [MockProcessRow()]
        self.mock_query_builder.trace_processor.query.return_value = mock_result
        
        # 测试属性访问
        assert self.accessor.name == "test_process"
        assert self.accessor.pid == 456
        assert self.accessor.upid == 789
        
        # 验证SQL查询
        call_args = self.mock_query_builder.trace_processor.query.call_args[0][0]
        assert "SELECT process.*" in call_args
        assert "FROM process_track" in call_args
        assert "JOIN process ON process_track.upid = process.upid" in call_args
        assert "WHERE process_track.id = 123" in call_args
    
    def test_process_attribute_access_no_result(self):
        """测试process属性访问无结果的情况"""
        self.mock_query_builder.trace_processor.query.return_value = []
        
        assert self.accessor.name is None
        assert self.accessor.pid is None
    
    def test_process_attribute_access_error(self):
        """测试process属性访问错误的情况"""
        self.mock_query_builder.trace_processor.query.side_effect = Exception("Query error")
        
        assert self.accessor.name is None


class TestThreadAccessor:
    """测试Thread访问器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.mock_query_builder = Mock()
        self.mock_slice = Mock()
        self.mock_slice.track_id = 123
        self.accessor = ThreadAccessor(self.mock_query_builder, self.mock_slice)
    
    def test_thread_attribute_access(self):
        """测试thread属性访问"""
        # 模拟thread查询结果
        class MockThreadRow:
            def __init__(self):
                self.name = "test_thread"
                self.tid = 456
                self.utid = 789
        
        mock_result = [MockThreadRow()]
        self.mock_query_builder.trace_processor.query.return_value = mock_result
        
        # 测试属性访问
        assert self.accessor.name == "test_thread"
        assert self.accessor.tid == 456
        assert self.accessor.utid == 789
        
        # 验证SQL查询
        call_args = self.mock_query_builder.trace_processor.query.call_args[0][0]
        assert "SELECT thread.*" in call_args
        assert "FROM thread_track" in call_args
        assert "JOIN thread ON thread_track.utid = thread.utid" in call_args
        assert "WHERE thread_track.id = 123" in call_args
    
    def test_thread_attribute_access_no_result(self):
        """测试thread属性访问无结果的情况"""
        self.mock_query_builder.trace_processor.query.return_value = []
        
        assert self.accessor.name is None
        assert self.accessor.tid is None


class TestSlice:
    """测试增强的Slice类"""
    
    def test_enhanced_slice_creation(self):
        """测试增强Slice对象创建"""
        enhanced_slice = Slice(
            id=1,
            name="test_slice",
            ts=1000000,
            dur=500000,
            pid=123,
            tid=456,
            cat="test",
            track_id=789
        )
        
        assert enhanced_slice.id == 1
        assert enhanced_slice.name == "test_slice"
        assert enhanced_slice.track_id == 789
    
    def test_related_objects_property(self):
        """测试related对象属性"""
        enhanced_slice = Slice(
            id=1, name="test", ts=1000, dur=500,
            pid=0, tid=0, cat="test", track_id=123
        )
        
        # 先设置query_builder
        mock_query_builder = Mock()
        enhanced_slice.set_query_builder(mock_query_builder)
        
        related = enhanced_slice.related
        assert isinstance(related, RelatedObjectsAccessor)
        assert related.slice_obj == enhanced_slice
    
    def test_set_query_builder(self):
        """测试设置query_builder"""
        enhanced_slice = Slice(
            id=1, name="test", ts=1000, dur=500,
            pid=0, tid=0, cat="test", track_id=123
        )
        
        mock_query_builder = Mock()
        enhanced_slice.set_query_builder(mock_query_builder)
        
        assert enhanced_slice.related.query_builder == mock_query_builder
    
    def test_track_property(self):
        """测试track属性"""
        enhanced_slice = Slice(
            id=1, name="test", ts=1000, dur=500,
            pid=0, tid=0, cat="test", track_id=123
        )
        
        mock_query_builder = Mock()
        enhanced_slice.set_query_builder(mock_query_builder)
        
        # 创建mock的track对象
        mock_track = Mock()
        mock_track.id = 123
        mock_track.name = "test_track"
        mock_track.type = "slice"
        mock_track.pid = 456
        mock_track.tid = 789
        mock_track.cat = "test"
        mock_track.args = None
        
        # 设置mock的链式调用
        mock_track_query = Mock()
        mock_track_query.first.return_value = mock_track
        mock_query_builder.track.return_value = mock_track_query
        
        track = enhanced_slice.track
        assert track is not None
        assert track.name == "test_track"
    
    def test_process_property(self):
        """测试process属性"""
        enhanced_slice = Slice(
            id=1, name="test", ts=1000, dur=500,
            pid=0, tid=0, cat="test", track_id=123
        )
        
        mock_query_builder = Mock()
        enhanced_slice.set_query_builder(mock_query_builder)
        
        process_accessor = enhanced_slice.process
        assert isinstance(process_accessor, ProcessAccessor)
    
    def test_thread_property(self):
        """测试thread属性"""
        enhanced_slice = Slice(
            id=1, name="test", ts=1000, dur=500,
            pid=0, tid=0, cat="test", track_id=123
        )
        
        mock_query_builder = Mock()
        enhanced_slice.set_query_builder(mock_query_builder)
        
        thread_accessor = enhanced_slice.thread
        assert isinstance(thread_accessor, ThreadAccessor)
