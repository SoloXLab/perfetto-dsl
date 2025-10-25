"""
Slice类的单元测试
"""

import pytest
from perfetto.dsl import Slice


class TestSlice:
    """Slice类测试"""
    
    def test_slice_creation(self):
        """测试Slice对象创建"""
        slice_obj = Slice(
            id=1,
            name="test_slice",
            ts=1000000,
            dur=500000,
            pid=123,
            tid=456,
            cat="test_category",
            track_id=789
        )
        
        assert slice_obj.id == 1
        assert slice_obj.name == "test_slice"
        assert slice_obj.ts == 1000000
        assert slice_obj.dur == 500000
        assert slice_obj.pid == 123
        assert slice_obj.tid == 456
        assert slice_obj.cat == "test_category"
        assert slice_obj.track_id == 789
    
    def test_time_properties(self):
        """测试时间相关属性"""
        slice_obj = Slice(
            id=1, name="test", ts=1000000, dur=500000,
            pid=0, tid=0, cat="test", track_id=0
        )
        
        # 纳秒属性
        assert slice_obj.start_time_ns == 1000000
        assert slice_obj.duration_ns == 500000
        assert slice_obj.end_time_ns == 1500000
        
        # 毫秒属性
        assert slice_obj.start_time_ms == 1.0
        assert slice_obj.duration_ms == 0.5
        assert slice_obj.end_time_ms == 1.5
    
    def test_overlaps_with(self):
        """测试slice重叠检测"""
        slice1 = Slice(
            id=1, name="slice1", ts=1000, dur=1000,
            pid=0, tid=0, cat="test", track_id=0
        )
        slice2 = Slice(
            id=2, name="slice2", ts=1500, dur=1000,
            pid=0, tid=0, cat="test", track_id=0
        )
        slice3 = Slice(
            id=3, name="slice3", ts=3000, dur=1000,
            pid=0, tid=0, cat="test", track_id=0
        )
        
        # slice1和slice2重叠
        assert slice1.overlaps_with(slice2) is True
        assert slice2.overlaps_with(slice1) is True
        
        # slice1和slice3不重叠
        assert slice1.overlaps_with(slice3) is False
        assert slice3.overlaps_with(slice1) is False
    
    def test_contains_timestamp(self):
        """测试时间戳包含检测"""
        slice_obj = Slice(
            id=1, name="test", ts=1000, dur=1000,
            pid=0, tid=0, cat="test", track_id=0
        )
        
        # 在范围内
        assert slice_obj.contains(1000) is True
        assert slice_obj.contains(1500) is True
        assert slice_obj.contains(1999) is True
        
        # 不在范围内
        assert slice_obj.contains(999) is False
        assert slice_obj.contains(2000) is False
    
    def test_get_arg(self):
        """测试参数获取"""
        # 有args的情况
        slice_obj = Slice(
            id=1, name="test", ts=1000, dur=1000,
            pid=0, tid=0, cat="test", track_id=0,
            args={"key1": "value1", "key2": 42}
        )
        
        assert slice_obj.get_arg("key1") == "value1"
        assert slice_obj.get_arg("key2") == 42
        assert slice_obj.get_arg("nonexistent") is None
        assert slice_obj.get_arg("nonexistent", "default") == "default"
        
        # 没有args的情况
        slice_obj_no_args = Slice(
            id=1, name="test", ts=1000, dur=1000,
            pid=0, tid=0, cat="test", track_id=0
        )
        
        assert slice_obj_no_args.get_arg("key1") is None
        assert slice_obj_no_args.get_arg("key1", "default") == "default"
    
    def test_to_dict(self):
        """测试转换为字典"""
        slice_obj = Slice(
            id=1, name="test", ts=1000, dur=1000,
            pid=0, tid=0, cat="test", track_id=0,
            args={"key": "value"}
        )
        
        result = slice_obj.to_dict()
        expected = {
            'id': 1,
            'name': 'test',
            'ts': 1000,
            'dur': 1000,
            'pid': 0,
            'tid': 0,
            'cat': 'test',
            'track_id': 0,
            'args': {'key': 'value'}
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'id': 1,
            'name': 'test',
            'ts': 1000,
            'dur': 1000,
            'pid': 0,
            'tid': 0,
            'cat': 'test',
            'track_id': 0,
            'args': {'key': 'value'}
        }
        
        slice_obj = Slice.from_dict(data)
        
        assert slice_obj.id == 1
        assert slice_obj.name == 'test'
        assert slice_obj.ts == 1000
        assert slice_obj.dur == 1000
        assert slice_obj.pid == 0
        assert slice_obj.tid == 0
        assert slice_obj.cat == 'test'
        assert slice_obj.track_id == 0
        assert slice_obj.args == {'key': 'value'}
    
    def test_from_dict_with_row_object(self):
        """测试从Row对象创建（模拟perfetto Row）"""
        class MockRow:
            def __init__(self):
                self.id = 1
                self.name = 'test'
                self.ts = 1000
                self.dur = 1000
                self.pid = 0
                self.tid = 0
                self.cat = 'test'
                self.track_id = 0
                self.args = None
        
        mock_row = MockRow()
        slice_obj = Slice.from_dict(mock_row)
        
        assert slice_obj.id == 1
        assert slice_obj.name == 'test'
        assert slice_obj.ts == 1000
        assert slice_obj.dur == 1000
        assert slice_obj.pid == 0
        assert slice_obj.tid == 0
        assert slice_obj.cat == 'test'
        assert slice_obj.track_id == 0
        assert slice_obj.args is None
    
    def test_string_representations(self):
        """测试字符串表示"""
        slice_obj = Slice(
            id=1, name="test_slice", ts=1000000, dur=500000,
            pid=0, tid=0, cat="test", track_id=0
        )
        
        str_repr = str(slice_obj)
        assert "Slice(id=1, name='test_slice', duration=0.50)" in str_repr
        
        repr_str = repr(slice_obj)
        assert "Slice(id=1, name='test_slice', ts=1000000" in repr_str
