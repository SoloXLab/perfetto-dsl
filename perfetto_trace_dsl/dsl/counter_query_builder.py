from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass


@dataclass
class Counter:
    """表示Perfetto中的一个counter（计数器）"""
    
    id: int
    name: str
    ts: int
    value: float
    track_id: int
    
    @property
    def timestamp_ns(self) -> int:
        """时间戳（纳秒）"""
        return self.ts
    
    @property
    def timestamp_ms(self) -> float:
        """时间戳（毫秒）"""
        return self.ts / 1_000_000
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'ts': self.ts,
            'value': self.value,
            'track_id': self.track_id
        }
    
    @classmethod
    def from_dict(cls, data) -> 'Counter':
        """从字典或Row对象创建Counter实例"""
        if hasattr(data, 'id'):
            return cls(
                id=getattr(data, 'id', 0),
                name=getattr(data, 'name', ''),
                ts=getattr(data, 'ts', 0),
                value=getattr(data, 'value', 0.0),
                track_id=getattr(data, 'track_id', 0)
            )
        else:
            return cls(
                id=data['id'],
                name=data['name'],
                ts=data['ts'],
                value=data['value'],
                track_id=data['track_id']
            )
    
    def __str__(self) -> str:
        return f"Counter(id={self.id}, name='{self.name}', ts={self.timestamp_ms:.2f}ms, value={self.value})"
    
    def __repr__(self) -> str:
        return f"Counter(id={self.id}, name='{self.name}', ts={self.ts}, value={self.value}, track_id={self.track_id})"


class CounterQueryBuilder:
    """Counter查询构建器，支持链式调用构建复杂的Perfetto counter查询"""
    
    def __init__(self, trace_processor, **kwargs):
        self.trace_processor = trace_processor
        self.sql_parts = []
        self.joins = []
        self.where_conditions = []
        self.current_table = "counter"
        self.result_type = Counter
        self._results = None
        self._executed = False
        self.limit_count = None
        self.order_by_clause = None
        
        # 构建基础查询，包含必要的JOIN
        sql = """
        SELECT 
            counter.*,
            counter_track.name as track_name,
            process.name as process_name,
            process.upid as process_id,
            counter_track.unit as unit
        FROM counter
        LEFT JOIN counter_track ON counter.track_id = counter_track.id
        LEFT JOIN process_counter_track ON counter_track.id = process_counter_track.id
        LEFT JOIN process ON process_counter_track.upid = process.upid
        """
        
        self.sql_parts = [sql]
        
        # 处理初始化参数
        for key, value in kwargs.items():
            self._add_condition(key, value)
    
    def _add_condition(self, key: str, value: Any):
        """添加查询条件"""
        if key == 'name':
            # name通过counter_track.name获取
            if isinstance(value, str):
                self.where_conditions.append(f"counter_track.name = '{value}'")
            else:
                self.where_conditions.append(f"counter_track.name = {value}")
        elif key == 'process_name':
            # process_name通过process.name获取
            if isinstance(value, str):
                self.where_conditions.append(f"process.name = '{value}'")
            else:
                self.where_conditions.append(f"process.name = {value}")
        elif key == 'process_id':
            # process_id通过process.upid获取
            self.where_conditions.append(f"process.upid = {value}")
        else:
            # 其他字段直接使用counter表的字段
            if isinstance(value, str):
                self.where_conditions.append(f"counter.{key} = '{value}'")
            else:
                self.where_conditions.append(f"counter.{key} = {value}")
    
    def name(self, name: Union[str, List[str], None] = None) -> 'CounterQueryBuilder':
        """按counter名称过滤"""
        if name is not None:
            if isinstance(name, str):
                self.where_conditions.append(f"counter_track.name = '{name}'")
            else:
                name_list = ','.join(f"'{n}'" for n in name)
                self.where_conditions.append(f"counter_track.name IN ({name_list})")
        return self
    
    def process(self, name: Union[str, List[str], None] = None) -> 'CounterQueryBuilder':
        """按进程名称过滤"""
        if name is not None:
            if isinstance(name, str):
                self.where_conditions.append(f"process.name = '{name}'")
            else:
                name_list = ','.join(f"'{n}'" for n in name)
                self.where_conditions.append(f"process.name IN ({name_list})")
        return self
    
    def track_id(self, track_id: Union[int, List[int], None] = None) -> 'CounterQueryBuilder':
        """按track ID过滤"""
        if track_id is not None:
            if isinstance(track_id, int):
                self.where_conditions.append(f"counter.track_id = {track_id}")
            else:
                track_list = ','.join(map(str, track_id))
                self.where_conditions.append(f"counter.track_id IN ({track_list})")
        return self
    
    def value_range(self, min_value: float = None, max_value: float = None) -> 'CounterQueryBuilder':
        """按counter值范围过滤"""
        if min_value is not None:
            self.where_conditions.append(f"counter.value >= {min_value}")
        if max_value is not None:
            self.where_conditions.append(f"counter.value <= {max_value}")
        return self
    
    def time_range(self, start_ts: int = None, end_ts: int = None) -> 'CounterQueryBuilder':
        """按时间范围过滤"""
        if start_ts is not None:
            self.where_conditions.append(f"counter.ts >= {start_ts}")
        if end_ts is not None:
            self.where_conditions.append(f"counter.ts <= {end_ts}")
        return self
    
    def limit(self, count: int) -> 'CounterQueryBuilder':
        """限制结果数量"""
        self.limit_count = count
        return self

    def _invalidate_cache(self):
        self._executed = False
        self._results = None
    
    def order_by(self, clause: str) -> 'CounterQueryBuilder':
        """添加排序条件"""
        self.order_by_clause = clause
        self._invalidate_cache()
        return self
    
    def _execute_query(self) -> List[Counter]:
        """执行查询并返回结果"""
        if self._executed:
            return self._results
        
        if not self.sql_parts:
            raise ValueError("No query specified")
        
        # 构建完整的SQL查询
        sql = self.sql_parts[0]
        
        # 添加WHERE条件
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        # 添加ORDER BY
        if self.order_by_clause:
            sql += f" ORDER BY {self.order_by_clause}"
        
        # 添加LIMIT
        if self.limit_count:
            sql += f" LIMIT {self.limit_count}"
        
        try:
            result = self.trace_processor.query(sql)
            self._results = [Counter.from_dict(row) for row in result]
            self._executed = True
            return self._results
        except Exception as e:
            raise RuntimeError(f"Failed to execute counter query: {e}")
    
    def all(self) -> List[Counter]:
        """获取全部结果，默认按 counter.ts ASC（时间升序）"""
        if self.order_by_clause is None:
            self.order_by_clause = "counter.ts ASC"
            self._invalidate_cache()
        return self._execute_query()

    def nth(self, n: int) -> Optional[Counter]:
        """返回第n个结果（0-based，支持负索引）"""
        results = self.all()
        if not results:
            return None
        if n < 0:
            n = len(results) + n
        if n < 0 or n >= len(results):
            return None
        return results[n]

    def first(self) -> Optional[Counter]:
        """获取第一个结果（时间升序）"""
        return self.nth(0)

    def second(self) -> Optional[Counter]:
        return self.nth(1)

    def third(self) -> Optional[Counter]:
        return self.nth(2)

    def last(self) -> Optional[Counter]:
        """获取最后一个结果（时间升序）"""
        return self.nth(-1)
    
    def count(self) -> int:
        """获取结果数量（使用 SQL COUNT，高效）"""
        sql = """
        SELECT COUNT(*) as counter_count
        FROM counter
        LEFT JOIN counter_track ON counter.track_id = counter_track.id
        LEFT JOIN process_counter_track ON counter_track.id = process_counter_track.id
        LEFT JOIN process ON process_counter_track.upid = process.upid
        """
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                return getattr(row, 'counter_count', 0)
            return 0
        except Exception as e:
            raise RuntimeError(f"Failed to execute counter count query: {e}")
    
    def max(self, field: str = 'value') -> Optional[float]:
        """获取指定字段的最大值"""
        if not self._executed:
            # 构建MAX查询
            sql = f"SELECT MAX(counter.{field}) as max_value FROM counter"
            sql += " LEFT JOIN counter_track ON counter.track_id = counter_track.id"
            sql += " LEFT JOIN process_counter_track ON counter_track.id = process_counter_track.id"
            sql += " LEFT JOIN process ON process_counter_track.upid = process.upid"
            
            if self.where_conditions:
                sql += " WHERE " + " AND ".join(self.where_conditions)
            
            try:
                result = self.trace_processor.query(sql)
                for row in result:
                    return getattr(row, 'max_value', None)
                return None
            except Exception as e:
                raise RuntimeError(f"Failed to execute max query: {e}")
        else:
            # 从已执行的结果中计算
            results = self._results
            if not results:
                return None
            return max(getattr(counter, field, 0) for counter in results)
    
    def min(self, field: str = 'value') -> Optional[float]:
        """获取指定字段的最小值"""
        if not self._executed:
            # 构建MIN查询
            sql = f"SELECT MIN(counter.{field}) as min_value FROM counter"
            sql += " LEFT JOIN counter_track ON counter.track_id = counter_track.id"
            sql += " LEFT JOIN process_counter_track ON counter_track.id = process_counter_track.id"
            sql += " LEFT JOIN process ON process_counter_track.upid = process.upid"
            
            if self.where_conditions:
                sql += " WHERE " + " AND ".join(self.where_conditions)
            
            try:
                result = self.trace_processor.query(sql)
                for row in result:
                    return getattr(row, 'min_value', None)
                return None
            except Exception as e:
                raise RuntimeError(f"Failed to execute min query: {e}")
        else:
            # 从已执行的结果中计算
            results = self._results
            if not results:
                return None
            return min(getattr(counter, field, 0) for counter in results)
    
    def avg(self, field: str = 'value') -> Optional[float]:
        """获取指定字段的平均值"""
        if not self._executed:
            # 构建AVG查询
            sql = f"SELECT AVG(counter.{field}) as avg_value FROM counter"
            sql += " LEFT JOIN counter_track ON counter.track_id = counter_track.id"
            sql += " LEFT JOIN process_counter_track ON counter_track.id = process_counter_track.id"
            sql += " LEFT JOIN process ON process_counter_track.upid = process.upid"
            
            if self.where_conditions:
                sql += " WHERE " + " AND ".join(self.where_conditions)
            
            try:
                result = self.trace_processor.query(sql)
                for row in result:
                    return getattr(row, 'avg_value', None)
                return None
            except Exception as e:
                raise RuntimeError(f"Failed to execute avg query: {e}")
        else:
            # 从已执行的结果中计算
            results = self._results
            if not results:
                return None
            values = [getattr(counter, field, 0) for counter in results]
            return sum(values) / len(values)
    
    def __iter__(self):
        """支持迭代（时间升序）"""
        return iter(self.all())
    
    def __getitem__(self, index):
        """支持索引访问（时间升序）"""
        return self.all()[index]
    
    def __len__(self):
        """支持len()函数"""
        return self.count()
    
    def __bool__(self):
        """支持布尔判断"""
        return self.count() > 0
    
    def __str__(self):
        """字符串表示"""
        results = self._execute_query()
        if len(results) == 0:
            return "CounterQueryBuilder: No results"
        else:
            result_strings = [str(result) for result in results]
            return '\n'.join(result_strings)
    
    def __repr__(self):
        """repr表示"""
        return f"CounterQueryBuilder(count={self.count()})"
