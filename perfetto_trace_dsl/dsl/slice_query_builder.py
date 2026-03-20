from typing import Dict, Any, Optional, Union, Set, List, TYPE_CHECKING, Tuple
from dataclasses import dataclass
import re

if TYPE_CHECKING:
    from .counter_query_builder import Counter
# EnhancedSlice 已合并到 Slice 中


class ArgsValues:
    """处理args值的统计操作"""
    
    def __init__(self, values: List[Any]):
        self.values = values
        self._filtered_values = None
    
    def _get_filtered_values(self):
        """获取过滤后的数值（排除None值）"""
        if self._filtered_values is None:
            self._filtered_values = [v for v in self.values if v is not None]
        return self._filtered_values
    
    def count(self) -> int:
        """返回值的总数（包括None）"""
        return len(self.values)
    
    def count_non_null(self) -> int:
        """返回非None值的数量"""
        return len(self._get_filtered_values())
    
    def max(self) -> Any:
        """返回最大值"""
        filtered = self._get_filtered_values()
        if not filtered:
            return None
        try:
            return max(filtered)
        except TypeError:
            # 如果无法比较，返回None
            return None
    
    def min(self) -> Any:
        """返回最小值"""
        filtered = self._get_filtered_values()
        if not filtered:
            return None
        try:
            return min(filtered)
        except TypeError:
            # 如果无法比较，返回None
            return None
    
    def avg(self) -> Optional[float]:
        """返回平均值（仅对数值类型有效）"""
        filtered = self._get_filtered_values()
        if not filtered:
            return None
        
        numeric_values = []
        for v in filtered:
            try:
                numeric_values.append(float(v))
            except (ValueError, TypeError):
                continue
        
        if not numeric_values:
            return None
        
        return sum(numeric_values) / len(numeric_values)
    
    def sum(self) -> Optional[float]:
        """返回总和（仅对数值类型有效）"""
        filtered = self._get_filtered_values()
        if not filtered:
            return None
        
        numeric_values = []
        for v in filtered:
            try:
                numeric_values.append(float(v))
            except (ValueError, TypeError):
                continue
        
        if not numeric_values:
            return None
        
        return sum(numeric_values)
    
    def unique(self) -> List[Any]:
        """返回唯一值列表"""
        filtered = self._get_filtered_values()
        seen = set()
        unique_values = []
        for v in filtered:
            # 使用字符串表示来比较，因为某些值可能不可哈希
            v_str = str(v)
            if v_str not in seen:
                seen.add(v_str)
                unique_values.append(v)
        return unique_values
    
    def unique_count(self) -> int:
        """返回唯一值的数量"""
        return len(self.unique())
    
    def __str__(self) -> str:
        """字符串表示"""
        return str(self.values)
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示"""
        return f"ArgsValues({self.values})"
    
    def __len__(self) -> int:
        """返回值的数量"""
        return len(self.values)
    
    def __getitem__(self, index):
        """支持索引访问"""
        return self.values[index]
    
    def __iter__(self):
        """支持迭代"""
        return iter(self.values)


@dataclass
class Track:
    """表示Perfetto中的一个track（轨道）"""
    
    id: int
    name: str
    type: str
    pid: Optional[int]
    tid: Optional[int]
    cat: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    
    def get_arg(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        if self.args is None:
            return default
        return self.args.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'pid': self.pid,
            'tid': self.tid,
            'cat': self.cat,
            'args': self.args
        }
    
    @classmethod
    def from_dict(cls, data) -> 'Track':
        """从字典或Row对象创建Track实例"""
        # 处理perfetto的Row对象（支持属性访问）
        if hasattr(data, 'id'):
            return cls(
                id=getattr(data, 'id', 0),
                name=getattr(data, 'name', ''),
                type=getattr(data, 'type', ''),
                pid=getattr(data, 'pid', None),
                tid=getattr(data, 'tid', None),
                cat=getattr(data, 'cat', None),
                args=getattr(data, 'args', None)
            )
        else:
            # 如果是普通字典
            return cls(
                id=data['id'],
                name=data['name'],
                type=data['type'],
                pid=data.get('pid'),
                tid=data.get('tid'),
                cat=data.get('cat'),
                args=data.get('args')
            )
    
    def __str__(self) -> str:
        return f"Track(id={self.id}, name='{self.name}', type='{self.type}')"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class Flow:
    """表示Perfetto中的一个flow（流）"""
    
    id: int
    slice_out: int
    slice_in: int
    name: Optional[str] = None
    args: Optional[Dict[str, Any]] = None
    type: Optional[str] = None
    category: Optional[str] = None
    ts: Optional[int] = None
    track_id: Optional[int] = None
    
    def get_arg(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        if self.args is None:
            return default
        return self.args.get(key, default)
    
    @property
    def flow_id(self) -> int:
        """OpenSpec兼容字段：flow_id"""
        return self.id
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'slice_out': self.slice_out,
            'slice_in': self.slice_in,
            'name': self.name,
            'args': self.args,
            'type': self.type,
            'category': self.category,
            'ts': self.ts,
            'track_id': self.track_id
        }
    
    @classmethod
    def from_dict(cls, data) -> 'Flow':
        """从字典或Row对象创建Flow实例"""
        # 处理perfetto的Row对象（支持属性访问）
        if hasattr(data, 'id'):
            return cls(
                id=getattr(data, 'id', 0),
                slice_out=getattr(data, 'slice_out', 0),
                slice_in=getattr(data, 'slice_in', 0),
                name=getattr(data, 'name', None),
                args=getattr(data, 'args', None),
                type=getattr(data, 'type', None),
                category=getattr(data, 'category', None),
                ts=getattr(data, 'ts', None),
                track_id=getattr(data, 'track_id', None)
            )
        else:
            # 如果是普通字典
            return cls(
                id=data['id'],
                slice_out=data['slice_out'],
                slice_in=data['slice_in'],
                name=data.get('name'),
                args=data.get('args'),
                type=data.get('type'),
                category=data.get('category'),
                ts=data.get('ts'),
                track_id=data.get('track_id')
            )
    
    def __str__(self) -> str:
        return f"Flow(id={self.id}, slice_out={self.slice_out}, slice_in={self.slice_in})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class FlowLink:
    """flow对端关系对象：对端slice + flow属性"""
    
    slice: 'Slice'
    flow: Flow


class _SliceArgComparator:
    """slice.arg(key) 返回的比较器"""

    def __init__(self, builder: 'SliceQueryBuilder', key: str):
        self._builder = builder
        self._key = key

    def compare(self, op: str, value: Any) -> 'SliceQueryBuilder':
        return self._builder._add_slice_arg_comparison(self._key, op, value)


class _FlowArgComparator:
    """flow.arg(key) 返回的比较器"""

    def __init__(self, builder: 'FlowLinkQueryBuilder', key: str):
        self._builder = builder
        self._key = key

    def compare(self, op: str, value: Any) -> 'FlowLinkQueryBuilder':
        return self._builder._add_flow_arg_comparison(self._key, op, value)


class RelatedObjectsAccessor:
    """关联对象访问器，提供懒加载的关联对象访问"""
    
    def __init__(self, query_builder: 'SliceQueryBuilder', slice_obj: 'Slice'):
        self._query_builder = query_builder
        self._slice = slice_obj
        self._process = None
        self._thread = None
        self._track = None
    
    @property
    def process(self):
        """获取关联的进程信息"""
        if self._process is None:
            # 通过 track 获取进程信息
            track = self.track
            if track and track.pid:
                # 查询进程信息
                result = self._query_builder.trace_processor.query(
                    f"SELECT * FROM process WHERE upid = {track.pid}"
                )
                if result:
                    row = result[0]
                    self._process = {
                        'upid': row.upid,
                        'name': row.name,
                        'pid': row.pid
                    }
        return self._process
    
    @property
    def thread(self):
        """获取关联的线程信息"""
        if self._thread is None:
            # 通过 track 获取线程信息
            track = self.track
            if track and track.tid:
                # 查询线程信息
                result = self._query_builder.trace_processor.query(
                    f"SELECT * FROM thread WHERE utid = {track.tid}"
                )
                if result:
                    row = result[0]
                    self._thread = {
                        'utid': row.utid,
                        'name': row.name,
                        'tid': row.tid,
                        'is_main_thread': row.is_main_thread
                    }
        return self._thread
    
    @property
    def track(self):
        """获取关联的轨道信息"""
        if self._track is None:
            # 直接查询 track 表
            result = self._query_builder.trace_processor.query(
                f"SELECT * FROM track WHERE id = {self._slice.track_id}"
            )
            if result:
                for row in result:
                    self._track = Track.from_dict(row)
                    break
        return self._track


class FlowLinkQueryBuilder:
    """针对单个slice的flow关联查询构建器，返回FlowLink对象"""

    _OPERATOR_MAP = {
        "==": "=",
        "=": "=",
        "!=": "!=",
        ">": ">",
        ">=": ">=",
        "<": "<",
        "<=": "<=",
        "like": "LIKE",
        "LIKE": "LIKE",
    }

    def __init__(self, trace_processor, base_slice: 'Slice', direction: str):
        if direction not in ("out", "in"):
            raise ValueError("direction must be 'out' or 'in'")
        self.trace_processor = trace_processor
        self.base_slice = base_slice
        self.direction = direction
        self.joins: List[str] = []
        self.where_conditions: List[str] = []
        self.limit_count: Optional[int] = None
        self.order_by_clause: Optional[str] = None
        self._executed = False
        self._results: Optional[List[FlowLink]] = None
        self._next_arg_alias = 0
        self._flow_columns: Optional[Set[str]] = None

    def _invalidate_cache(self):
        self._executed = False
        self._results = None

    def _normalize_operator(self, op: str) -> str:
        if op not in self._OPERATOR_MAP:
            raise ValueError(f"Unsupported operator: {op}")
        return self._OPERATOR_MAP[op]

    def _sql_literal(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _get_flow_columns(self) -> Set[str]:
        if self._flow_columns is not None:
            return self._flow_columns
        columns: Set[str] = set()
        try:
            rows = self.trace_processor.query("PRAGMA table_info(flow)")
            for row in rows:
                name = getattr(row, "name", None)
                if name is None and hasattr(row, "__getitem__"):
                    try:
                        name = row[1]
                    except Exception:
                        name = None
                if name:
                    columns.add(name)
        except Exception:
            # 在mock环境中可能不存在PRAGMA，保留最小列集合
            columns = {"id", "slice_out", "slice_in", "name", "arg_set_id"}
        self._flow_columns = columns
        return columns

    def _flow_col_or_null(self, col: str, alias: str) -> str:
        if col in self._get_flow_columns():
            return f"flow.{col} AS {alias}"
        return f"NULL AS {alias}"

    def name(self, value: str) -> 'FlowLinkQueryBuilder':
        self.where_conditions.append(f"flow.name = {self._sql_literal(value)}")
        self._invalidate_cache()
        return self

    def arg(self, key: str) -> _FlowArgComparator:
        return _FlowArgComparator(self, key)

    def _add_flow_arg_comparison(self, key: str, op: str, value: Any) -> 'FlowLinkQueryBuilder':
        normalized = self._normalize_operator(op)
        if "arg_set_id" not in self._get_flow_columns():
            # 当前trace的flow表无arg_set_id时，不可能命中flow args条件
            self.where_conditions.append("1 = 0")
            self._invalidate_cache()
            return self

        alias = f"flow_args_{self._next_arg_alias}"
        self._next_arg_alias += 1
        self.joins.append(f"JOIN args {alias} ON flow.arg_set_id = {alias}.arg_set_id")

        key_condition = f"{alias}.key = {self._sql_literal(key)}"
        if isinstance(value, str):
            value_condition = f"{alias}.string_value {normalized} {self._sql_literal(value)}"
        elif value is None:
            value_condition = f"{alias}.display_value IS NULL" if normalized == "=" else f"{alias}.display_value IS NOT NULL"
        else:
            numeric_literal = self._sql_literal(value)
            value_condition = f"(COALESCE({alias}.int_value, {alias}.real_value) {normalized} {numeric_literal})"

        self.where_conditions.append(f"({key_condition} AND {value_condition})")
        self._invalidate_cache()
        return self

    def order_by(self, clause: str) -> 'FlowLinkQueryBuilder':
        self.order_by_clause = clause
        self._invalidate_cache()
        return self

    def limit(self, count: int) -> 'FlowLinkQueryBuilder':
        self.limit_count = count
        self._invalidate_cache()
        return self

    def all(self) -> List[FlowLink]:
        """获取全部结果，默认按 peer.ts ASC（时间升序）"""
        if self.order_by_clause is None:
            self.order_by_clause = "peer.ts ASC"
            self._invalidate_cache()
        return self._execute_query()

    def first(self) -> Optional[FlowLink]:
        return self.nth(0)

    def nth(self, n: int) -> Optional[FlowLink]:
        links = self.all()
        if not links:
            return None
        if n < 0:
            n = len(links) + n
        if n < 0 or n >= len(links):
            return None
        return links[n]

    def second(self) -> Optional[FlowLink]:
        return self.nth(1)

    def third(self) -> Optional[FlowLink]:
        return self.nth(2)

    def last(self) -> Optional[FlowLink]:
        return self.nth(-1)

    def count(self) -> int:
        return len(self.all())

    def _build_sql(self) -> str:
        peer_join = "JOIN slice peer ON flow.slice_in = peer.id" if self.direction == "out" else "JOIN slice peer ON flow.slice_out = peer.id"
        base_condition = f"flow.slice_out = {self.base_slice.id}" if self.direction == "out" else f"flow.slice_in = {self.base_slice.id}"

        select_parts = [
            "peer.*",
            "flow.id AS flow_id",
            "flow.slice_out AS flow_slice_out",
            "flow.slice_in AS flow_slice_in",
            self._flow_col_or_null("name", "flow_name"),
            self._flow_col_or_null("type", "flow_type"),
            self._flow_col_or_null("category", "flow_category"),
            self._flow_col_or_null("ts", "flow_ts"),
            self._flow_col_or_null("track_id", "flow_track_id"),
            self._flow_col_or_null("arg_set_id", "flow_arg_set_id"),
        ]

        sql = "SELECT " + ", ".join(select_parts) + " FROM flow "
        sql += peer_join
        for join in self.joins:
            sql += f" {join}"

        all_conditions = [base_condition] + self.where_conditions
        if all_conditions:
            sql += " WHERE " + " AND ".join(all_conditions)
        if self.order_by_clause:
            sql += f" ORDER BY {self.order_by_clause}"
        if self.limit_count is not None:
            sql += f" LIMIT {self.limit_count}"
        return sql

    def _query_flow_args(self, arg_set_id: Optional[int]) -> Optional[Dict[str, Any]]:
        if arg_set_id is None:
            return None
        try:
            rows = self.trace_processor.query(
                f"SELECT key, value_type, int_value, string_value, real_value, display_value FROM args WHERE arg_set_id = {arg_set_id}"
            )
        except Exception:
            return None

        result: Dict[str, Any] = {}
        for row in rows:
            key = getattr(row, "key", None)
            if key is None:
                continue
            value_type = getattr(row, "value_type", None)
            if value_type == "int":
                value = getattr(row, "int_value", None)
            elif value_type == "real":
                value = getattr(row, "real_value", None)
            elif value_type == "string":
                value = getattr(row, "string_value", None)
            else:
                value = getattr(row, "display_value", None)
            result[key] = value
        return result if result else None

    def _execute_query(self) -> List[FlowLink]:
        if self._executed:
            return self._results or []

        sql = self._build_sql()
        try:
            rows = self.trace_processor.query(sql)
        except Exception as e:
            raise RuntimeError(f"Failed to execute flow link query: {e}")

        results: List[FlowLink] = []
        for row in rows:
            peer_slice = Slice.from_dict(row)
            if self.base_slice._query_builder is not None:
                peer_slice.set_query_builder(self.base_slice._query_builder)

            flow = Flow(
                id=getattr(row, "flow_id", 0),
                slice_out=getattr(row, "flow_slice_out", 0),
                slice_in=getattr(row, "flow_slice_in", 0),
                name=getattr(row, "flow_name", None),
                type=getattr(row, "flow_type", None),
                category=getattr(row, "flow_category", None),
                ts=getattr(row, "flow_ts", None),
                track_id=getattr(row, "flow_track_id", None),
                args=self._query_flow_args(getattr(row, "flow_arg_set_id", None)),
            )
            results.append(FlowLink(slice=peer_slice, flow=flow))

        self._results = results
        self._executed = True
        return results


class SliceQueryBuilder:
    """查询构建器，支持链式调用构建复杂的Perfetto查询，支持懒加载"""
    
    def __init__(self, trace_processor):
        self.trace_processor = trace_processor
        self.sql_parts = []
        self.joins = []
        self.where_conditions = []
        self.current_table = None
        self.result_type = None
        self._results = None
        self._executed = False
        self.limit_count = None
        self.order_by_clause = None
        self._offset = None
        self._next_arg_alias = 0

    _OPERATOR_MAP = {
        "==": "=",
        "=": "=",
        "!=": "!=",
        ">": ">",
        ">=": ">=",
        "<": "<",
        "<=": "<=",
        "like": "LIKE",
        "LIKE": "LIKE",
    }

    def _invalidate_cache(self):
        self._executed = False
        self._results = None

    def _normalize_operator(self, op: str) -> str:
        if op not in self._OPERATOR_MAP:
            raise ValueError(f"Unsupported operator: {op}")
        return self._OPERATOR_MAP[op]

    def _sql_literal(self, value: Any) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def _add_field_comparison(self, field: str, op: str, value: Any, table_alias: str = "slice") -> 'SliceQueryBuilder':
        operator = self._normalize_operator(op)
        self.where_conditions.append(f"{table_alias}.{field} {operator} {self._sql_literal(value)}")
        self._invalidate_cache()
        return self

    def _apply_sugar_comparison(self, field: str, spec: Any):
        if not isinstance(spec, (tuple, list)) or len(spec) != 2:
            raise ValueError(f"{field} filter must be tuple/list like ('>=', value)")
        op, value = spec
        self._add_field_comparison(field, op, value, "slice")
    
    def slice(self, **kwargs) -> 'SliceQueryBuilder':
        """添加slice查询条件"""
        kwargs = dict(kwargs)

        self.current_table = "slice"
        self.result_type = Slice
        self.sql_parts = ["SELECT slice.* FROM slice"]
        self.joins = []
        self.where_conditions = []
        self.limit_count = None
        self.order_by_clause = None
        self._offset = None
        self._next_arg_alias = 0
        self._invalidate_cache()

        # OpenSpec 语法糖
        ts_spec = kwargs.pop("ts", None)
        dur_spec = kwargs.pop("dur", None)
        depth_spec = kwargs.pop("depth", None)
        args_spec = kwargs.pop("args", None)
        before_spec = kwargs.pop("before", None)
        after_spec = kwargs.pop("after", None)
        between_spec = kwargs.pop("between", None)
        flow_out_name = kwargs.pop("flow_out_name", None)
        flow_out_arg = kwargs.pop("flow_out_arg", None)
        kwargs.pop("include_args", None)
        
        # 检查是否有args相关的过滤条件
        args_filters = {}
        for key, value in kwargs.items():
            if key.startswith('args_'):
                args_filters[key[5:]] = value  # 移除'args_'前缀
        
        # 如果有args过滤条件，添加args表的JOIN
        if args_filters:
            self.joins.append("JOIN args ON slice.arg_set_id = args.arg_set_id")
        
        for key, value in kwargs.items():
            if key == "include_args":
                continue  # 跳过 include_args 参数
            elif key.startswith('args_'):
                # 处理args过滤条件
                arg_key = key[5:].replace('_', ' ')  # 移除'args_'前缀并将下划线替换为空格
                if isinstance(value, str):
                    self.where_conditions.append(f"args.key = '{arg_key}' AND args.string_value LIKE '{value}'")
                else:
                    self.where_conditions.append(f"args.key = '{arg_key}' AND args.int_value = {value}")
            elif key == "name" and isinstance(value, str):
                # 检查是否包含特殊语法符号
                if '|' in value:
                    # 包含特殊语法，使用特殊语法解析
                    try:
                        parsed = self._parse_slice_spec(value)
                        
                        # 添加名称过滤条件
                        name_pattern = parsed['name']
                        if not name_pattern.startswith('%'):
                            name_pattern = f'%{name_pattern}'
                        if not name_pattern.endswith('%'):
                            name_pattern = f'{name_pattern}%'
                        self.where_conditions.append(f"slice.name LIKE '{name_pattern}'")
                        
                        # 添加进程过滤条件
                        if parsed['process']:
                            self.joins.append("JOIN track ON slice.track_id = track.id")
                            self.joins.append("LEFT JOIN process_track ON track.id = process_track.id")
                            self.joins.append("LEFT JOIN process ON process_track.upid = process.upid")
                            self.joins.append("LEFT JOIN thread_track ON track.id = thread_track.id")
                            self.joins.append("LEFT JOIN thread ON thread_track.utid = thread.utid")
                            self.joins.append("LEFT JOIN process p2 ON thread.upid = p2.upid")
                            
                            # 进程名匹配（支持通配符）
                            process_pattern = parsed['process']
                            if not process_pattern.startswith('%'):
                                process_pattern = f'%{process_pattern}%'
                            self.where_conditions.append(f"(process.name LIKE '{process_pattern}' OR p2.name LIKE '{process_pattern}')")
                        
                        # 添加线程过滤条件
                        if parsed['thread']:
                            if parsed['thread'] == 'main':
                                # 主线程
                                self.where_conditions.append("thread.is_main_thread = 1")
                            else:
                                # 线程名匹配
                                thread_pattern = parsed['thread']
                                if not thread_pattern.startswith('%'):
                                    thread_pattern = f'%{thread_pattern}%'
                                self.where_conditions.append(f"thread.name LIKE '{thread_pattern}'")
                        
                        # 添加Track过滤条件
                        if parsed['track']:
                            # 确保有track JOIN
                            if not any("JOIN track" in join for join in self.joins):
                                self.joins.append("JOIN track ON slice.track_id = track.id")
                            
                            # Track名匹配
                            track_pattern = parsed['track']
                            if not track_pattern.startswith('%'):
                                track_pattern = f'%{track_pattern}%'
                            self.where_conditions.append(f"track.name LIKE '{track_pattern}'")
                        
                        # 添加图层过滤条件
                        if parsed['layer']:
                            # 确保有args JOIN
                            if not any("JOIN args" in join for join in self.joins):
                                self.joins.append("JOIN args ON slice.arg_set_id = args.arg_set_id")
                            
                            # 图层名匹配（通过Layer name参数）
                            layer_pattern = parsed['layer']
                            if not layer_pattern.startswith('%'):
                                layer_pattern = f'%{layer_pattern}%'
                            self.where_conditions.append(f"args.key = 'Layer name' AND args.string_value LIKE '{layer_pattern}'")
                        
                        # 处理索引（如果有的话）
                        if parsed['index'] is not None:
                            if parsed['index'] == -1:
                                # 最后一个
                                self.order_by_clause = "slice.ts DESC"
                                self.limit_count = 1
                            else:
                                # 指定索引（从0开始）
                                self.order_by_clause = "slice.ts ASC"
                                self.limit_count = 1
                                self._offset = parsed['index']
                        
                    except Exception:
                        # 如果特殊语法解析失败，回退到常规name匹配
                        # 注意：这里不应该添加name过滤条件，因为已经在特殊语法解析中添加了
                        pass
                else:
                    # 保持兼容：slice(name=...) 默认模糊匹配
                    if not value.startswith('%'):
                        value = f'%{value}'
                    if not value.endswith('%'):
                        value = f'{value}%'
                    self.where_conditions.append(f"slice.name LIKE {self._sql_literal(value)}")
            elif key == "duration_ms":
                # 处理持续时间过滤
                if isinstance(value, (int, float)):
                    self.where_conditions.append(f"slice.dur >= {int(value * 1_000_000)}")
                elif isinstance(value, dict):
                    if "min" in value:
                        self.where_conditions.append(f"slice.dur >= {int(value['min'] * 1_000_000)}")
                    if "max" in value:
                        self.where_conditions.append(f"slice.dur <= {int(value['max'] * 1_000_000)}")
            else:
                if isinstance(value, str):
                    self.where_conditions.append(f"slice.{key} LIKE '{value}'")
                else:
                    self.where_conditions.append(f"slice.{key} = {value}")

        if ts_spec is not None:
            self._apply_sugar_comparison("ts", ts_spec)
        if dur_spec is not None:
            self._apply_sugar_comparison("dur", dur_spec)
        if depth_spec is not None:
            self._apply_sugar_comparison("depth", depth_spec)

        if args_spec is not None:
            if not isinstance(args_spec, dict):
                raise ValueError("slice(args=...) expects a dict")
            for key, value in args_spec.items():
                self.arg(key).compare("==", value)

        if after_spec is not None:
            self.after(after_spec)
        if before_spec is not None:
            self.before(before_spec)
        if between_spec is not None:
            if isinstance(between_spec, (tuple, list)):
                if len(between_spec) == 1:
                    self.between(between_spec[0])
                elif len(between_spec) == 2:
                    self.between(between_spec[0], between_spec[1])
                else:
                    raise ValueError("between sugar expects 1 or 2 boundaries")
            else:
                self.between(between_spec)

        if flow_out_name is not None or flow_out_arg is not None:
            self._add_flow_out_exists_filter(flow_out_name, flow_out_arg)
        
        return self

    # ===== OpenSpec 基础属性链式接口 =====
    def id(self, value: int) -> 'SliceQueryBuilder':
        return self._add_field_comparison("id", "==", value)

    def name(self, value: str) -> 'SliceQueryBuilder':
        if "%" in value:
            self.where_conditions.append(f"slice.name LIKE {self._sql_literal(value)}")
        else:
            self.where_conditions.append(f"slice.name = {self._sql_literal(value)}")
        self._invalidate_cache()
        return self

    def ts(self, op: str, value: Union[int, float]) -> 'SliceQueryBuilder':
        return self._add_field_comparison("ts", op, value)

    def dur(self, op: str, value: Union[int, float]) -> 'SliceQueryBuilder':
        return self._add_field_comparison("dur", op, value)

    def depth(self, op: str, value: Union[int, float]) -> 'SliceQueryBuilder':
        return self._add_field_comparison("depth", op, value)

    def arg(self, key: str) -> _SliceArgComparator:
        return _SliceArgComparator(self, key)

    def _add_slice_arg_comparison(self, key: str, op: str, value: Any) -> 'SliceQueryBuilder':
        operator = self._normalize_operator(op)
        alias = f"args_cmp_{self._next_arg_alias}"
        self._next_arg_alias += 1
        self.joins.append(f"JOIN args {alias} ON slice.arg_set_id = {alias}.arg_set_id")

        key_condition = f"{alias}.key = {self._sql_literal(key)}"
        if isinstance(value, str):
            value_condition = f"{alias}.string_value {operator} {self._sql_literal(value)}"
        elif value is None:
            value_condition = f"{alias}.display_value IS NULL" if operator == "=" else f"{alias}.display_value IS NOT NULL"
        else:
            value_condition = f"(COALESCE({alias}.int_value, {alias}.real_value) {operator} {self._sql_literal(value)})"

        self.where_conditions.append(f"({key_condition} AND {value_condition})")
        self._invalidate_cache()
        return self

    def descendants(self, **kwargs) -> 'SliceQueryBuilder':
        """查询所有子孙slice（递归）"""
        if self.current_table != "slice":
            raise ValueError("descendants() can only be called after slice()")

        base_sql = self._build_query_sql(self)
        self.sql_parts = [f"""
        WITH RECURSIVE descendant_tree(id) AS (
            SELECT child.id
            FROM slice child
            WHERE child.parent_id IN (SELECT base.id FROM ({base_sql}) base)
            UNION ALL
            SELECT child.id
            FROM slice child
            JOIN descendant_tree dt ON child.parent_id = dt.id
        )
        SELECT slice.* FROM slice
        JOIN descendant_tree dt ON slice.id = dt.id
        """.strip()]
        self.joins = []
        self.where_conditions = []
        self._offset = None
        self._invalidate_cache()

        for key, value in kwargs.items():
            if isinstance(value, str):
                self.where_conditions.append(f"slice.{key} LIKE {self._sql_literal(value)}")
            else:
                self.where_conditions.append(f"slice.{key} = {self._sql_literal(value)}")

        return self

    def _add_flow_out_exists_filter(self, flow_name: Optional[str], flow_args: Optional[Dict[str, Any]]):
        flow_args = flow_args or {}
        if not isinstance(flow_args, dict):
            raise ValueError("flow_out_arg expects a dict")

        subquery_joins: List[str] = []
        subquery_conditions: List[str] = ["f.slice_out = slice.id"]
        if flow_name is not None:
            subquery_conditions.append(f"f.name = {self._sql_literal(flow_name)}")

        for i, (key, value) in enumerate(flow_args.items()):
            alias = f"farg_{i}"
            subquery_joins.append(f"JOIN args {alias} ON f.arg_set_id = {alias}.arg_set_id")
            key_condition = f"{alias}.key = {self._sql_literal(key)}"
            if isinstance(value, str):
                value_condition = f"{alias}.string_value = {self._sql_literal(value)}"
            else:
                value_condition = f"COALESCE({alias}.int_value, {alias}.real_value) = {self._sql_literal(value)}"
            subquery_conditions.append(f"({key_condition} AND {value_condition})")

        subquery = "SELECT 1 FROM flow f"
        if subquery_joins:
            subquery += " " + " ".join(subquery_joins)
        subquery += " WHERE " + " AND ".join(subquery_conditions)

        self.where_conditions.append(f"EXISTS ({subquery})")
        self._invalidate_cache()
    
    def process(self, **kwargs) -> 'SliceQueryBuilder':
        """添加process查询条件"""
        if self.current_table not in ["slice", "slice_out", "slice_in"]:
            raise ValueError("process() can only be called after slice(), flow_out(), or flow_in()")
        
        # 根据 current_table 确定要关联的 slice 表
        slice_table = self.current_table
        
        self.joins.append(f"JOIN process_track ON {slice_table}.track_id = process_track.id")
        self.joins.append("JOIN process ON process_track.upid = process.upid")
        
        # 修改SQL查询以包含process.pid字段
        if self.sql_parts and "SELECT" in self.sql_parts[0]:
            if "process.pid" not in self.sql_parts[0]:
                self.sql_parts[0] = self.sql_parts[0].replace("FROM", ", process.pid FROM")
        
        for key, value in kwargs.items():
            if isinstance(value, str):
                # 对于字符串值，使用 LIKE 匹配以支持通配符
                self.where_conditions.append(f"process.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"process.{key} = {value}")
        
        return self
    
    def thread(self, **kwargs) -> 'SliceQueryBuilder':
        """添加thread查询条件"""
        if self.current_table not in ["slice", "slice_out", "slice_in"]:
            raise ValueError("thread() can only be called after slice(), flow_out(), or flow_in()")
        
        # 根据 current_table 确定要关联的 slice 表
        slice_table = self.current_table
        
        # 检查是否已经有process join，如果有则移除
        process_joins_to_remove = []
        for i, join in enumerate(self.joins):
            if "process_track" in join or "process" in join:
                process_joins_to_remove.append(i)
        
        # 从后往前移除，避免索引问题
        for i in reversed(process_joins_to_remove):
            self.joins.pop(i)
        
        # 添加thread相关的join
        self.joins.append(f"JOIN thread_track ON {slice_table}.track_id = thread_track.id")
        self.joins.append("JOIN thread ON thread_track.utid = thread.utid")
        
        # 如果需要process信息，通过thread.upid关联
        self.joins.append("JOIN process ON thread.upid = process.upid")
        
        # 修改SQL查询以包含thread.tid和process.pid字段
        if self.sql_parts and "SELECT" in self.sql_parts[0]:
            if "thread.tid" not in self.sql_parts[0]:
                self.sql_parts[0] = self.sql_parts[0].replace("FROM", ", thread.tid FROM")
            if "process.pid" not in self.sql_parts[0]:
                self.sql_parts[0] = self.sql_parts[0].replace("FROM", ", process.pid FROM")
        
        for key, value in kwargs.items():
            if key in ['main', 'main_thread'] and value is True:
                # 主线程：使用thread.is_main_thread字段
                self.where_conditions.append("thread.is_main_thread = 1")
            elif isinstance(value, str):
                # 对于字符串值，使用 LIKE 匹配以支持通配符
                self.where_conditions.append(f"thread.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"thread.{key} = {value}")
        
        return self
    
    def parent(self, level: int = 1, **kwargs) -> 'SliceQueryBuilder':
        """添加parent查询条件"""
        if self.current_table != "slice":
            raise ValueError("parent() can only be called after slice()")
        
        # 构建parent查询的JOIN
        if level == 1:
            # 直接父节点
            self.joins.append("JOIN slice parent_slice ON slice.parent_id = parent_slice.id")
        elif level > 1:
            # 多层父节点，使用递归CTE
            self._add_parent_cte(level)
        elif level == -1:
            # level=-1表示根据slice的depth来确定level值
            # 直接通过parent_id查找父节点
            self.joins.append("JOIN slice parent_slice ON slice.parent_id = parent_slice.id")
        
        # 修改SQL查询以返回parent_slice
        if self.sql_parts and "SELECT" in self.sql_parts[0]:
            self.sql_parts[0] = self.sql_parts[0].replace("slice.*", "parent_slice.*")
        
        # 添加额外的过滤条件
        for key, value in kwargs.items():
            if isinstance(value, str):
                self.where_conditions.append(f"parent_slice.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"parent_slice.{key} = {value}")
        
        return self
    
    def _add_parent_cte(self, level: int):
        """添加多层父节点查询的CTE"""
        # 使用递归CTE来查找多层父节点
        cte_sql = f"""
        WITH RECURSIVE parent_hierarchy AS (
            SELECT id, parent_id, 0 as level
            FROM slice
            WHERE id IN (SELECT id FROM slice WHERE parent_id IS NOT NULL)
            
            UNION ALL
            
            SELECT s.id, s.parent_id, ph.level + 1
            FROM slice s
            JOIN parent_hierarchy ph ON s.id = ph.parent_id
            WHERE ph.level < {level}
        )
        """
        
        # 将CTE添加到查询中
        if not hasattr(self, '_ctes'):
            self._ctes = []
        self._ctes.append(cte_sql)
        
        # 添加JOIN到parent_hierarchy
        self.joins.append("JOIN parent_hierarchy ph ON slice.id = ph.id")
        self.joins.append("JOIN slice parent_slice ON ph.parent_id = parent_slice.id")
    
    def _add_dynamic_parent_cte(self):
        """添加动态父节点查询，根据slice的depth来确定level值"""
        # 使用递归CTE来查找父节点，level等于slice的depth
        cte_sql = """
        WITH RECURSIVE parent_hierarchy AS (
            SELECT id, parent_id, 0 as level, depth
            FROM slice
            WHERE parent_id IS NOT NULL
            
            UNION ALL
            
            SELECT s.id, s.parent_id, ph.level + 1, s.depth
            FROM slice s
            JOIN parent_hierarchy ph ON s.id = ph.parent_id
            WHERE ph.level < s.depth
        )
        """
        
        # 将CTE添加到查询中
        if not hasattr(self, '_ctes'):
            self._ctes = []
        self._ctes.append(cte_sql)
        
        # 添加JOIN到parent_hierarchy，根据depth确定level
        self.joins.append("JOIN parent_hierarchy ph ON slice.id = ph.id AND ph.level = slice.depth")
        self.joins.append("JOIN slice parent_slice ON ph.parent_id = parent_slice.id")
    
    def child(self, level: int = 1, **kwargs) -> 'SliceQueryBuilder':
        """添加child查询条件"""
        if self.current_table != "slice":
            raise ValueError("child() can only be called after slice()")
        
        # 构建child查询的JOIN
        if level == 1:
            # 直接子节点
            self.joins.append("JOIN slice child_slice ON child_slice.parent_id = slice.id")
        elif level > 1:
            # 多层子节点，使用递归CTE
            self._add_child_cte(level)
        elif level < 0:
            # 负级别表示向下查找所有子节点
            self._add_child_cte(abs(level))
        
        # 修改SQL查询以返回child_slice
        if self.sql_parts and "SELECT" in self.sql_parts[0]:
            self.sql_parts[0] = self.sql_parts[0].replace("slice.*", "child_slice.*")
        
        # 添加额外的过滤条件
        for key, value in kwargs.items():
            if isinstance(value, str):
                self.where_conditions.append(f"child_slice.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"child_slice.{key} = {value}")
        
        return self
    
    def _add_child_cte(self, level: int):
        """添加多层子节点查询的CTE"""
        # 使用递归CTE来查找多层子节点
        cte_sql = f"""
        WITH RECURSIVE child_hierarchy AS (
            SELECT id, parent_id, 0 as level
            FROM slice
            WHERE parent_id IN (SELECT id FROM slice)
            
            UNION ALL
            
            SELECT s.id, s.parent_id, ch.level + 1
            FROM slice s
            JOIN child_hierarchy ch ON s.parent_id = ch.id
            WHERE ch.level < {level - 1}
        )
        """
        
        # 将CTE添加到查询中
        if not hasattr(self, '_ctes'):
            self._ctes = []
        self._ctes.append(cte_sql)
        
        # 添加JOIN到child_hierarchy
        self.joins.append("JOIN child_hierarchy ch ON slice.id = ch.parent_id")
        self.joins.append("JOIN slice child_slice ON ch.id = child_slice.id")
    
    def siblings(self, **kwargs) -> 'SliceQueryBuilder':
        """添加siblings查询条件"""
        if self.current_table != "slice":
            raise ValueError("siblings() can only be called after slice()")
        
        # 构建siblings查询的JOIN
        self.joins.append("JOIN slice sibling_slice ON sibling_slice.parent_id = slice.parent_id AND sibling_slice.id != slice.id")
        
        # 修改SQL查询以返回sibling_slice
        if self.sql_parts and "SELECT" in self.sql_parts[0]:
            self.sql_parts[0] = self.sql_parts[0].replace("slice.*", "sibling_slice.*")
        
        # 添加额外的过滤条件
        for key, value in kwargs.items():
            if isinstance(value, str):
                self.where_conditions.append(f"sibling_slice.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"sibling_slice.{key} = {value}")
        
        return self
    
    def filter(self, condition: str) -> 'SliceQueryBuilder':
        """添加自定义过滤条件"""
        if self.current_table != "slice":
            raise ValueError("filter() can only be called after slice()")
        
        # 直接添加自定义条件
        self.where_conditions.append(condition)
        return self
    
    def args(self, **kwargs) -> 'SliceQueryBuilder':
        """添加args查询条件"""
        if self.current_table != "slice":
            raise ValueError("args() can only be called after slice()")
        
        # 为每个args参数添加单独的JOIN
        for i, (key, value) in enumerate(kwargs.items()):
            # 将下划线替换为空格，因为args的key通常包含空格
            arg_key = key.replace('_', ' ')
            alias = f"args_{i}" if i > 0 else "args"
            
            # 添加args表的JOIN
            self.joins.append(f"JOIN args {alias} ON slice.arg_set_id = {alias}.arg_set_id")
            
            # 添加args过滤条件
            if isinstance(value, str):
                self.where_conditions.append(f"{alias}.key = '{arg_key}' AND {alias}.string_value LIKE '{value}'")
            elif isinstance(value, (int, float)):
                self.where_conditions.append(f"{alias}.key = '{arg_key}' AND {alias}.int_value = {value}")
            else:
                self.where_conditions.append(f"{alias}.key = '{arg_key}' AND {alias}.value = '{value}'")
        
        return self
    
    def frame_id(self, default: int = None) -> 'SliceQueryBuilder':
        """过滤包含frame_id的slice"""
        if self.current_table != "slice":
            raise ValueError("frame_id() can only be called after slice()")
        
        # 使用正则表达式匹配Choreographer#doFrame后面的数字
        # 这里使用SQL的REGEXP函数（如果支持）或者LIKE模式
        self.where_conditions.append("slice.name REGEXP 'Choreographer#doFrame\\s+[0-9]+'")
        return self
    
    def input_id(self, default: str = None) -> 'SliceQueryBuilder':
        """过滤包含input_id的slice"""
        if self.current_table != "slice":
            raise ValueError("input_id() can only be called after slice()")
        
        # 使用正则表达式匹配id=0x开头的十六进制值
        # 这里使用SQL的REGEXP函数（如果支持）或者LIKE模式
        self.where_conditions.append("slice.name REGEXP 'id=0x[0-9a-fA-F]+'")
        return self
    
    def flow_out(self, **kwargs) -> 'SliceQueryBuilder':
        """查找通过 flow 关联的 slice_out（输出 slice）"""
        if self.current_table != "slice":
            raise ValueError("flow_out() can only be called after slice()")
        
        # 在修改 joins 之前检查是否有 process 或 thread JOIN
        has_process_join = any("process" in join for join in self.joins)
        has_thread_join = any("thread" in join for join in self.joins)
        
        # 修改查询以返回 slice_out，并更新 current_table
        self.sql_parts = ["SELECT slice_out.* FROM slice"]
        self.joins.append("JOIN flow ON slice.id = flow.slice_out")
        self.joins.append("JOIN slice slice_out ON flow.slice_in = slice_out.id")
        
        # 暂时不添加复杂的JOIN，只添加基本的flow查询
        # 后续可以通过其他方法获取process、thread信息
        
        # 更新 current_table 为 slice_out，这样后续的 process/thread/track 等方法会正确应用过滤条件
        self.current_table = "slice_out"
        
        # 添加额外的过滤条件
        for key, value in kwargs.items():
            if isinstance(value, str):
                # 对于字符串值，使用 LIKE 匹配以支持通配符
                self.where_conditions.append(f"slice_out.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"slice_out.{key} = {value}")
        
        return self
    
    def flow_in(self, **kwargs) -> 'SliceQueryBuilder':
        """查找通过 flow 关联的 slice_in（输入 slice）"""
        if self.current_table != "slice":
            raise ValueError("flow_in() can only be called after slice()")
        
        # 在修改 joins 之前检查是否有 process 或 thread JOIN
        has_process_join = any("process" in join for join in self.joins)
        has_thread_join = any("thread" in join for join in self.joins)
        
        # 修改查询以返回 slice_in，并更新 current_table
        self.sql_parts = ["SELECT slice_in.* FROM slice"]
        self.joins.append("JOIN flow ON slice.id = flow.slice_in")
        self.joins.append("JOIN slice slice_in ON flow.slice_out = slice_in.id")
        
        # 暂时不添加复杂的JOIN，只添加基本的flow查询
        # 后续可以通过其他方法获取process、thread信息
        
        # 更新 current_table 为 slice_in，这样后续的 process/thread/track 等方法会正确应用过滤条件
        self.current_table = "slice_in"
        
        # 添加额外的过滤条件
        for key, value in kwargs.items():
            if isinstance(value, str):
                # 对于字符串值，使用 LIKE 匹配以支持通配符
                self.where_conditions.append(f"slice_in.{key} LIKE '{value}'")
            else:
                self.where_conditions.append(f"slice_in.{key} = {value}")
        
        return self
    
    def track(self, **kwargs) -> 'SliceQueryBuilder':
        """添加track查询条件"""
        if self.current_table in ["slice", "slice_out", "slice_in"]:
            # 如果当前是 slice 查询，添加 track 相关的 JOIN 和过滤条件
            # 根据 current_table 确定要关联的 slice 表
            slice_table = self.current_table
            
            # 检查是否已经有 track 相关的 JOIN
            has_track_join = any("JOIN track" in join for join in self.joins)
            
            if not has_track_join:
                # 添加 track JOIN
                self.joins.append(f"JOIN track ON {slice_table}.track_id = track.id")
            
            # 添加 track 过滤条件
            for key, value in kwargs.items():
                if isinstance(value, str):
                    # 对于字符串值，使用 LIKE 匹配以支持通配符
                    self.where_conditions.append(f"track.{key} LIKE '{value}'")
                else:
                    self.where_conditions.append(f"track.{key} = {value}")
        else:
            # 如果是独立的 track 查询
            self.current_table = "track"
            self.result_type = Track
            self.sql_parts = ["SELECT track.* FROM track"]
            
            for key, value in kwargs.items():
                if isinstance(value, str):
                    # 对于字符串值，使用 LIKE 匹配以支持通配符
                    self.where_conditions.append(f"track.{key} LIKE '{value}'")
                else:
                    self.where_conditions.append(f"track.{key} = {value}")
        
        return self
    
    def limit(self, count: int) -> 'SliceQueryBuilder':
        """限制结果数量"""
        self.limit_count = count
        return self
    
    def order_by(self, clause: str) -> 'SliceQueryBuilder':
        """添加排序条件"""
        self.order_by_clause = clause
        return self
    
    def first(self):
        """获取第一个结果"""
        results = self._execute_query()
        return results[0] if results else None
    
    def last(self):
        """获取最后一个结果"""
        results = self._execute_query()
        return results[-1] if results else None
    
    def count(self) -> int:
        """
        获取查询结果的数量
        
        Returns:
            int: 结果数量
        """
        if self.current_table == "slice":
            return self._slice_count()
        elif self.current_table == "counter":
            return self._counter_count()
        else:
            # 通用计数方法
            results = self._execute_query()
            return len(results)
    
    def _slice_count(self) -> int:
        """
        获取slice查询结果的数量
        
        Returns:
            int: slice数量
        """
        
        # 构建计数查询，使用 COUNT(DISTINCT slice.id) 避免 args JOIN 导致的重复计数
        sql = "SELECT COUNT(DISTINCT slice.id) as slice_count FROM slice"
        
        for join in self.joins:
            sql += f" {join}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                return getattr(row, 'slice_count', 0)
            return 0
        except Exception as e:
            raise RuntimeError(f"Failed to execute slice count query: {e}")
    
    def _counter_count(self) -> int:
        """
        获取counter查询结果的数量
        
        Returns:
            int: counter数量
        """
        # 构建计数查询，使用与counter查询相同的JOIN结构
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
    
    def max(self, field: str = None) -> float:
        """
        获取指定字段的最大值
        
        Args:
            field: 要计算最大值的字段
                - 对于slice查询，默认为'duration'
                - 对于counter查询，默认为'value'
            
        Returns:
            float: 最大值
        """
        if self.current_table == "slice":
            if field is None:
                field = 'duration'
            return self._slice_max(field)
        elif self.current_table == "counter":
            if field is None:
                field = 'value'
            return self._counter_max(field)
        else:
            raise ValueError("max() method is only available for slice or counter queries")
    
    def _slice_max(self, field: str = 'duration') -> float:
        """
        获取slice指定字段的最大值
        
        Args:
            field: 要计算最大值的字段，默认为'duration'
            
        Returns:
            float: 最大值（毫秒）
        """
        
        # 构建聚合查询
        if field == 'duration':
            sql = "SELECT MAX(slice.dur / 1000000.0) as max_duration FROM slice"
        else:
            sql = f"SELECT MAX(slice.{field}) as max_value FROM slice"
        
        for join in self.joins:
            sql += f" {join}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                if field == 'duration':
                    return getattr(row, 'max_duration', None)
                else:
                    return getattr(row, 'max_value', None)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to execute slice max query: {e}")
    
    def min(self, field: str = None) -> float:
        """
        获取指定字段的最小值
        
        Args:
            field: 要计算最小值的字段
                - 对于slice查询，默认为'duration'
                - 对于counter查询，默认为'value'
            
        Returns:
            float: 最小值
        """
        if self.current_table == "slice":
            if field is None:
                field = 'duration'
            return self._slice_min(field)
        elif self.current_table == "counter":
            if field is None:
                field = 'value'
            return self._counter_min(field)
        else:
            raise ValueError("min() method is only available for slice or counter queries")
    
    def _slice_min(self, field: str = 'duration') -> float:
        """
        获取slice指定字段的最小值
        
        Args:
            field: 要计算最小值的字段，默认为'duration'
            
        Returns:
            float: 最小值（毫秒）
        """
        
        # 构建聚合查询
        if field == 'duration':
            sql = "SELECT MIN(slice.dur / 1000000.0) as min_duration FROM slice"
        else:
            sql = f"SELECT MIN(slice.{field}) as min_value FROM slice"
        
        for join in self.joins:
            sql += f" {join}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                if field == 'duration':
                    return getattr(row, 'min_duration', None)
                else:
                    return getattr(row, 'min_value', None)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to execute slice min query: {e}")
    
    def avg(self, field: str = None) -> float:
        """
        获取指定字段的平均值
        
        Args:
            field: 要计算平均值的字段
                - 对于slice查询，默认为'duration'
                - 对于counter查询，默认为'value'
            
        Returns:
            float: 平均值
        """
        if self.current_table == "slice":
            if field is None:
                field = 'duration'
            return self._slice_avg(field)
        elif self.current_table == "counter":
            if field is None:
                field = 'value'
            return self._counter_avg(field)
        else:
            raise ValueError("avg() method is only available for slice or counter queries")
    
    def _slice_avg(self, field: str = 'duration') -> float:
        """
        获取slice指定字段的平均值
        
        Args:
            field: 要计算平均值的字段，默认为'duration'
            
        Returns:
            float: 平均值（毫秒）
        """
        
        # 构建聚合查询
        if field == 'duration':
            sql = "SELECT AVG(slice.dur / 1000000.0) as avg_duration FROM slice"
        else:
            sql = f"SELECT AVG(slice.{field}) as avg_value FROM slice"
        
        for join in self.joins:
            sql += f" {join}"
        
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                if field == 'duration':
                    return getattr(row, 'avg_duration', None)
                else:
                    return getattr(row, 'avg_value', None)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to execute slice avg query: {e}")
    
    def p90(self, field: str = 'duration') -> float:
        """
        获取slice指定字段的90百分位数
        
        Args:
            field: 要计算百分位数的字段，默认为'duration'
            
        Returns:
            float: 90百分位数（毫秒）
        """
        if self.current_table != "slice":
            raise ValueError("p90() method is only available for slice queries")
        
        return self._calculate_percentile(field, 90)
    
    def p95(self, field: str = 'duration') -> float:
        """
        获取slice指定字段的95百分位数
        
        Args:
            field: 要计算百分位数的字段，默认为'duration'
            
        Returns:
            float: 95百分位数（毫秒）
        """
        if self.current_table != "slice":
            raise ValueError("p95() method is only available for slice queries")
        
        return self._calculate_percentile(field, 95)
    
    def median(self, field: str = 'duration') -> float:
        """
        获取slice指定字段的中值（50百分位数）
        
        Args:
            field: 要计算中值的字段，默认为'duration'
            
        Returns:
            float: 中值（毫秒）
        """
        if self.current_table != "slice":
            raise ValueError("median() method is only available for slice queries")
        
        return self._calculate_percentile(field, 50)
    
    def _calculate_percentile(self, field: str, percentile: int) -> float:
        """
        计算指定字段的百分位数
        
        Args:
            field: 要计算百分位数的字段
            percentile: 百分位数（0-100）
            
        Returns:
            float: 百分位数值（毫秒）
        """
        try:
            # 获取所有数据并计算百分位数
            all_slices = self._execute_query()
            if not all_slices:
                return None
            
            # 提取字段值
            if field == 'duration':
                values = [slice.duration_ms for slice in all_slices]
            else:
                values = [getattr(slice, field, 0) for slice in all_slices]
            
            # 排序
            values.sort()
            
            # 计算百分位数
            if not values:
                return None
            
            index = (percentile / 100.0) * (len(values) - 1)
            if index.is_integer():
                return values[int(index)]
            else:
                lower = values[int(index)]
                upper = values[int(index) + 1]
                return lower + (upper - lower) * (index - int(index))
                
        except Exception as e:
            raise RuntimeError(f"Failed to execute percentile query: {e}")
    
    def _execute_query(self):
        """内部方法：执行查询并缓存结果"""
        if self._executed:
            return self._results
        
        if not self.sql_parts:
            raise ValueError("No query specified")
        
        # 构建完整的SQL查询
        sql = self._build_complete_sql()
        
        try:
            result = self.trace_processor.query(sql)
            results = []
            
            for row in result:
                if self.result_type == Slice:
                    enhanced_slice = Slice.from_dict(row)
                    enhanced_slice.set_query_builder(self)
                    results.append(enhanced_slice)
                elif self.result_type == Counter:
                    results.append(Counter.from_dict(row))
                elif self.result_type == Track:
                    results.append(Track.from_dict(row))
                elif self.result_type == Flow:
                    results.append(Flow.from_dict(row))
                else:
                    results.append(row)
            
            self._results = results
            self._executed = True
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}")
    
    def _build_complete_sql(self) -> str:
        """构建完整的SQL查询"""
        # 处理CTE
        cte_sql = ""
        if hasattr(self, '_ctes') and self._ctes:
            cte_sql = " ".join(self._ctes) + " "
        
        # 构建基础SQL
        sql = cte_sql + self.sql_parts[0]
        
        # 添加JOIN
        for join in self.joins:
            sql += f" {join}"
        
        # 添加WHERE条件
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        # 添加ORDER BY
        if self.order_by_clause:
            sql += f" ORDER BY {self.order_by_clause}"
        
        # 添加OFFSET和LIMIT
        if hasattr(self, '_offset') and self._offset is not None:
            sql += f" OFFSET {self._offset}"
        
        if self.limit_count:
            sql += f" LIMIT {self.limit_count}"
        
        return sql
    
    def _print_empty_query_sql(self):
        """打印空查询的SQL语句"""
        if not self.sql_parts:
            print("No query specified")
            return
        
        sql = self._build_complete_sql()
        print("Generated SQL:")
        print(sql)
    
    def __iter__(self):
        """支持迭代 - 懒加载"""
        results = self._execute_query()
        return iter(results)
    
    def __getitem__(self, index):
        """支持索引访问 - 懒加载"""
        results = self._execute_query()
        return results[index]
    
    def __len__(self):
        """支持len()函数 - 懒加载"""
        results = self._execute_query()
        return len(results)
    
    def __bool__(self):
        """支持布尔判断 - 懒加载"""
        results = self._execute_query()
        return len(results) > 0
    
    def __str__(self):
        """字符串表示 - 懒加载，直接输出slice列表"""
        results = self._execute_query()
        if len(results) == 0:
            # 当没有结果时，打印SQL查询语句用于调试
            sql = self._build_complete_sql()
            return f"{self.result_type.__name__}SliceQueryBuilder: No results\nSQL: {sql}"
        else:
            # 直接输出所有结果的字符串表示
            result_strings = [str(result) for result in results]
            return '\n'.join(result_strings)
    
    def __repr__(self):
        """repr表示 - 懒加载"""
        return self.__str__()
    
    def counter(self, **kwargs) -> 'SliceQueryBuilder':
        """
        添加counter查询条件，支持通过关联表查询
        
        支持的查询参数:
        - id: counter的id
        - name: counter的名称（通过counter_track.name获取）
        - track_id: counter的track_id
        - ts: 时间戳
        - value: counter值
        - process_name: 进程名称（通过process_counter_track和process获取）
        - process_id: 进程ID
        """
        from .counter_query_builder import Counter
        self.current_table = "counter"
        self.result_type = Counter
        
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
        
        # 处理查询条件
        for key, value in kwargs.items():
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
        
        return self
    
    
    def flow(self, **kwargs) -> 'SliceQueryBuilder':
        """添加flow查询条件"""
        self.current_table = "flow"
        self.result_type = Flow
        self.sql_parts = ["SELECT flow.* FROM flow"]
        
        for key, value in kwargs.items():
            if isinstance(value, str):
                self.where_conditions.append(f"flow.{key} = '{value}'")
            else:
                self.where_conditions.append(f"flow.{key} = {value}")
        
        return self
    
    def args(self, key: Optional[str] = None, value: Any = None) -> Any:
        """
        处理args相关操作
        
        Args:
            key: 如果提供，返回指定key的值；如果不提供，返回完整的args字典
            value: 如果提供，则进行args过滤，返回匹配的slice列表
            
        Returns:
            如果key为None且value为None，返回所有slice的args字典列表
            如果只有key，返回所有slice对应key的值列表
            如果key和value都有，返回匹配的slice列表（SliceQueryBuilder）
            
        Examples:
            # 获取所有slice的args字典列表
            args_list = builder.args()
            
            # 获取所有slice对应key的值列表
            values = builder.args("Surface frame token")
            
            # 使用args进行过滤
            filtered_builder = builder.args("Surface frame token", 906975)
        """
        # 确保当前表是slice
        if self.current_table != "slice":
            raise ValueError("args() method is only available for slice queries")
        
        # 如果提供了value，进行过滤
        if value is not None:
            # 添加args表的JOIN（如果还没有的话）
            if not any("JOIN args" in join for join in self.joins):
                self.joins.append("JOIN args ON slice.arg_set_id = args.arg_set_id")
            
            # 添加过滤条件
            if isinstance(value, str):
                self.where_conditions.append(f"args.key = '{key}' AND args.string_value LIKE '%{value}%'")
            else:
                self.where_conditions.append(f"args.key = '{key}' AND args.int_value = {value}")
            
            return self
        
        # 如果没有提供value，执行查询并处理args
        results = self._execute_query()
        if not results:
            return []
        
        # 如果提供了key，返回所有slice对应key的值列表
        if key is not None:
            values = []
            for slice_obj in results:
                args_dict = slice_obj.get_args()
                if args_dict and key in args_dict:
                    values.append(args_dict[key])
                else:
                    values.append(None)
            return ArgsValues(values)
        
        # 如果没有提供key，返回所有slice的args字典列表
        args_list = []
        for slice_obj in results:
            args_dict = slice_obj.get_args()
            args_list.append(args_dict)
        return args_list
    
    def limit(self, count: int) -> 'SliceQueryBuilder':
        """添加LIMIT子句"""
        self.limit_count = count
        return self
    
    def order_by(self, clause: str) -> 'SliceQueryBuilder':
        """添加ORDER BY子句"""
        self.order_by_clause = clause
        return self
    
    def where(self, condition: str) -> 'SliceQueryBuilder':
        """添加WHERE条件"""
        self.where_conditions.append(condition)
        return self
    
    def filter(self, condition: str) -> 'SliceQueryBuilder':
        """
        添加过滤条件，支持简化的语法
        
        Args:
            condition: 过滤条件字符串，支持以下格式：
                - "duration>=1.0" - duration大于等于1.0ms
                - "duration>1.0" - duration大于1.0ms
                - "duration<10.0" - duration小于10.0ms
                - "duration<=10.0" - duration小于等于10.0ms
                - "duration=1.0" - duration等于1.0ms
                - "duration!=1.0" - duration不等于1.0ms
                - "name='slice_name'" - 名称等于指定值
                - "id=123" - ID等于指定值
        
        Returns:
            SliceQueryBuilder: 支持链式调用
        """
        # 解析过滤条件
        parsed_condition = self._parse_filter_condition(condition)
        self.where_conditions.append(parsed_condition)
        return self
    
    def _parse_filter_condition(self, condition: str) -> str:
        """
        解析过滤条件字符串
        
        Args:
            condition: 过滤条件字符串
            
        Returns:
            str: 解析后的SQL条件
        """
        import re
        
        # 处理duration相关的条件
        duration_pattern = r'duration\s*([><=!]+)\s*([\d.]+)'
        match = re.match(duration_pattern, condition)
        if match:
            operator = match.group(1).strip()
            value = float(match.group(2))
            # 将毫秒转换为纳秒
            nanoseconds = int(value * 1_000_000)
            
            if operator == '>':
                return f"slice.dur > {nanoseconds}"
            elif operator == '>=':
                return f"slice.dur >= {nanoseconds}"
            elif operator == '<':
                return f"slice.dur < {nanoseconds}"
            elif operator == '<=':
                return f"slice.dur <= {nanoseconds}"
            elif operator == '=':
                return f"slice.dur = {nanoseconds}"
            elif operator == '!=':
                return f"slice.dur != {nanoseconds}"
        
        # 处理其他字段的条件
        # 匹配格式: field operator value
        field_pattern = r'(\w+)\s*([><=!]+)\s*(.+)'
        match = re.match(field_pattern, condition)
        if match:
            field = match.group(1).strip()
            operator = match.group(2).strip()
            value = match.group(3).strip()
            
            # 处理字符串值（去除引号）
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
                return f"slice.{field} {operator} '{value}'"
            else:
                return f"slice.{field} {operator} {value}"
        
        # 如果无法解析，直接返回原条件
        return condition
    
    def before(self, slice_obj) -> 'SliceQueryBuilder':
        """
        添加before过滤条件，查找在指定slice开始时间之前的slice
        
        Args:
            slice_obj: Slice对象、SliceQueryBuilder对象或字符串（slice名称）
        
        Returns:
            SliceQueryBuilder: 支持链式调用
        """
        if self.current_table != "slice":
            raise ValueError("before() method is only available for slice queries")
        
        # 如果传入的是字符串，自动构建slice查询
        if isinstance(slice_obj, str):
            slice_obj = self._create_slice_query_from_name(slice_obj)
        
        # 构建before条件
        before_condition = self._build_before_condition(slice_obj)
        self.where_conditions.append(before_condition)
        return self
    
    def after(self, slice_obj) -> 'SliceQueryBuilder':
        """
        添加after过滤条件，查找在指定slice结束时间之后的slice
        
        Args:
            slice_obj: Slice对象、SliceQueryBuilder对象或字符串（slice名称）
        
        Returns:
            SliceQueryBuilder: 支持链式调用
        """
        if self.current_table != "slice":
            raise ValueError("after() method is only available for slice queries")
        
        # 如果传入的是字符串，自动构建slice查询
        if isinstance(slice_obj, str):
            slice_obj = self._create_slice_query_from_name(slice_obj)
        
        # 构建after条件
        after_condition = self._build_after_condition(slice_obj)
        self.where_conditions.append(after_condition)
        return self
    
    def between(self, start_slice, end_slice=None) -> 'SliceQueryBuilder':
        """
        添加between过滤条件，查找在指定时间范围内的slice
        
        Args:
            start_slice: 开始slice对象、SliceQueryBuilder对象或字符串（slice名称）
            end_slice: 结束slice对象、SliceQueryBuilder对象或字符串（slice名称），如果为None则使用start_slice的时间范围
        
        Returns:
            SliceQueryBuilder: 支持链式调用
        """
        if self.current_table != "slice":
            raise ValueError("between() method is only available for slice queries")
        
        # 如果传入的是字符串，自动构建slice查询
        if isinstance(start_slice, str):
            start_slice = self._create_slice_query_from_name(start_slice)
        
        if isinstance(end_slice, str):
            end_slice = self._create_slice_query_from_name(end_slice)
        
        # 构建between条件
        between_condition = self._build_between_condition(start_slice, end_slice)
        self.where_conditions.append(between_condition)
        return self
    
    def _create_slice_query_from_name(self, slice_name: str) -> 'SliceQueryBuilder':
        """
        根据slice名称创建一个新的SliceQueryBuilder实例
        支持新语法: <slice名字字符串>@<所在进程名>@@<所在线程名/或main表示主线程>@@@<所在Track名>#<第几个, 0表示第一个, -1表示最后一个, 1表示第二个, 2表示第三个...>
        
        Args:
            slice_name: slice的名称，支持以下格式：
                - "playing" - 简单名称匹配
                - "playing|com.example.app" - 带进程名
                - "playing|com.example.app||main" - 带进程名和主线程
                - "playing|com.example.app||main|||track_name" - 带进程名、线程名和Track名
                - "playing|com.example.app||main|||track_name#1" - 完整语法，指定第二个
                - "playing|com.example.app||main|||track_name#-1" - 完整语法，指定最后一个
            
        Returns:
            SliceQueryBuilder: 新的SliceQueryBuilder实例，用于查询指定名称的slice
        """
        # 解析slice名称
        parsed = self._parse_slice_spec(slice_name)
        
        # 创建新的SliceQueryBuilder实例
        new_builder = SliceQueryBuilder(self.trace_processor)
        new_builder.current_table = "slice"
        new_builder.result_type = Slice
        new_builder.sql_parts = ["SELECT slice.* FROM slice"]
        
        # 添加名称过滤条件
        name_pattern = parsed['name']
        if not name_pattern.startswith('%'):
            name_pattern = f'%{name_pattern}'
        if not name_pattern.endswith('%'):
            name_pattern = f'{name_pattern}%'
        new_builder.where_conditions.append(f"slice.name LIKE '{name_pattern}'")
        
        # 添加进程过滤条件
        if parsed['process']:
            new_builder.joins.append("JOIN track ON slice.track_id = track.id")
            new_builder.joins.append("LEFT JOIN process_track ON track.id = process_track.id")
            new_builder.joins.append("LEFT JOIN process ON process_track.upid = process.upid")
            new_builder.joins.append("LEFT JOIN thread_track ON track.id = thread_track.id")
            new_builder.joins.append("LEFT JOIN thread ON thread_track.utid = thread.utid")
            new_builder.joins.append("LEFT JOIN process p2 ON thread.upid = p2.upid")
            
            # 进程名匹配（支持通配符）
            if not parsed['process'].startswith('%'):
                parsed['process'] = f'%{parsed["process"]}%'
            new_builder.where_conditions.append(f"(process.name LIKE '{parsed['process']}' OR p2.name LIKE '{parsed['process']}')")
        
        # 添加线程过滤条件
        if parsed['thread']:
            # 确保有必要的 JOIN
            if not any("JOIN track" in join for join in new_builder.joins):
                new_builder.joins.append("JOIN track ON slice.track_id = track.id")
            if not any("JOIN thread_track" in join for join in new_builder.joins):
                new_builder.joins.append("LEFT JOIN thread_track ON track.id = thread_track.id")
            if not any("JOIN thread" in join for join in new_builder.joins):
                new_builder.joins.append("LEFT JOIN thread ON thread_track.utid = thread.utid")
            
            if parsed['thread'] == 'main':
                # 主线程
                new_builder.where_conditions.append("thread.is_main_thread = 1")
            else:
                # 线程名匹配
                if not parsed['thread'].startswith('%'):
                    parsed['thread'] = f'%{parsed["thread"]}%'
                new_builder.where_conditions.append(f"thread.name LIKE '{parsed['thread']}'")
        
        # 添加Track过滤条件
        if parsed['track']:
            # Track名匹配
            if not parsed['track'].startswith('%'):
                parsed['track'] = f'%{parsed["track"]}%'
            new_builder.where_conditions.append(f"track.name LIKE '{parsed['track']}'")
        
        # 添加图层过滤条件
        if parsed['layer']:
            # 确保有args JOIN
            if not any("JOIN args" in join for join in new_builder.joins):
                new_builder.joins.append("JOIN args ON slice.arg_set_id = args.arg_set_id")
            
            # 图层名匹配（通过Layer name参数）
            layer_pattern = parsed['layer']
            if not layer_pattern.startswith('%'):
                layer_pattern = f'%{layer_pattern}%'
            new_builder.where_conditions.append(f"args.key = 'Layer name' AND args.string_value LIKE '{layer_pattern}'")
        
        # 检查匹配的slice数量
        count_builder = SliceQueryBuilder(self.trace_processor)
        count_builder.current_table = "slice"
        count_builder.sql_parts = ["SELECT COUNT(*) as slice_count FROM slice"]
        count_builder.joins = new_builder.joins.copy()
        count_builder.where_conditions = new_builder.where_conditions.copy()
        
        try:
            count_result = count_builder._execute_query()
            slice_count = count_result[0].slice_count if count_result else 0
            
            if slice_count == 0:
                # 没有匹配的slice，返回空查询
                new_builder.where_conditions.append("1 = 0")  # 永远不匹配的条件
            elif slice_count == 1:
                # 只有一个匹配的slice，直接使用
                new_builder.order_by_clause = "slice.ts ASC"
                new_builder.limit_count = 1
            else:
                # 多个匹配的slice
                if parsed['index'] is not None:
                    # 如果指定了索引，使用索引
                    if parsed['index'] == -1:
                        # 最后一个
                        new_builder.order_by_clause = "slice.ts DESC"
                        new_builder.limit_count = 1
                    else:
                        # 指定索引（从0开始）
                        new_builder.order_by_clause = "slice.ts ASC"
                        new_builder.limit_count = 1
                        new_builder._offset = parsed['index']
                else:
                    # 没有指定索引，需要显式报错
                    self._raise_multiple_slices_error(slice_name, new_builder, slice_count)
        except ValueError:
            # 重新抛出ValueError（多slice错误）
            raise
        except Exception as e:
            # 如果查询失败，回退到原来的逻辑
            if parsed['index'] is not None:
                if parsed['index'] == -1:
                    # 最后一个
                    new_builder.order_by_clause = "slice.ts DESC"
                    new_builder.limit_count = 1
                else:
                    # 指定索引（从0开始）
                    new_builder.order_by_clause = "slice.ts ASC"
                    new_builder.limit_count = 1
                    new_builder._offset = parsed['index']
        
        return new_builder
    
    def _raise_multiple_slices_error(self, slice_name: str, query_builder: 'SliceQueryBuilder', slice_count: int):
        """
        当匹配到多个slice时抛出错误，并显示所有匹配的slice信息
        
        Args:
            slice_name: 原始slice名称
            query_builder: 查询构建器
            slice_count: 匹配的slice数量
        """
        # 获取所有匹配的slice信息
        try:
            # 创建查询所有匹配slice的构建器
            all_slices_builder = SliceQueryBuilder(self.trace_processor)
            all_slices_builder.current_table = "slice"
            all_slices_builder.result_type = Slice
            all_slices_builder.sql_parts = ["SELECT slice.* FROM slice"]
            all_slices_builder.joins = query_builder.joins.copy()
            all_slices_builder.where_conditions = query_builder.where_conditions.copy()
            all_slices_builder.order_by_clause = "slice.ts ASC"
            all_slices_builder.limit_count = 10  # 限制显示前10个
            
            # 执行查询获取slice信息
            matching_slices = all_slices_builder._execute_query()
            
            # 构建错误信息
            error_msg = f"匹配到 {slice_count} 个slice，请指定索引。匹配的slice信息：\n"
            error_msg += f"原始查询: {slice_name}\n\n"
            
            for i, slice_obj in enumerate(matching_slices):
                error_msg += f"索引 {i}: {slice_obj}\n"
            
            if slice_count > 10:
                error_msg += f"... 还有 {slice_count - 10} 个slice未显示\n"
            
            error_msg += f"\n请使用以下语法指定索引：\n"
            error_msg += f"- {slice_name}#0  (第一个)\n"
            error_msg += f"- {slice_name}#1  (第二个)\n"
            error_msg += f"- {slice_name}#-1 (最后一个)\n"
            
            raise ValueError(error_msg)
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise e
            else:
                # 如果获取slice信息失败，抛出简单的错误
                raise ValueError(f"匹配到 {slice_count} 个slice，请指定索引。使用语法: {slice_name}#<索引>")
    
    def _parse_slice_spec(self, slice_spec: str) -> dict:
        """
        解析slice规格字符串
        
        语法: <slice名字字符串>|<所在进程名>||<所在线程名/或main表示主线程>|||<所在Track名>||||<图层名>#<第几个, 0表示第一个, -1表示最后一个, 1表示第二个, 2表示第三个...>
        
        Args:
            slice_spec: slice规格字符串
            
        Returns:
            dict: 包含解析结果的字典
                - name: slice名称
                - process: 进程名（可选）
                - thread: 线程名（可选）
                - track: Track名（可选）
                - layer: 图层名（可选）
                - index: 索引（可选，None表示不指定）
        """
        result = {
            'name': slice_spec,
            'process': None,
            'thread': None,
            'track': None,
            'layer': None,
            'index': None
        }
        
        # 检查是否包含|符号（进程信息）
        # 需要按分隔符数量从多到少进行分割，避免误分割
        if slice_spec.startswith('||||'):
            # 以||||开头，只有图层信息
            layer_name = slice_spec[4:]  # 移除开头的||||
            result['layer'] = layer_name if layer_name else None
            result['process'] = None
            result['thread'] = None
            result['track'] = None
        elif '||||' in slice_spec:
            # 包含图层信息
            parts = slice_spec.split('||||', 1)
            if len(parts) == 2:
                # 前半部分包含slice名称、进程、线程、Track信息
                name_and_context_part = parts[0]
                layer_part = parts[1] if parts[1] else None
                
                # 检查图层部分是否包含索引
                if layer_part and '#' in layer_part:
                    # 使用rsplit找到最后一个#，检查后面是否跟有效数字
                    layer_name_part, index_part = layer_part.rsplit('#', 1)
                    
                    # 检查index_part是否为空或包含非数字字符
                    if not index_part or not index_part.strip():
                        # #后面没有内容，视为图层名称的一部分
                        result['layer'] = layer_part
                    else:
                        # 检查是否为有效数字
                        index_part = index_part.strip()
                        try:
                            index_value = int(index_part)
                            # 验证索引值的有效性
                            if index_value == -1 or index_value >= 0:
                                result['index'] = index_value
                                result['layer'] = layer_name_part if layer_name_part else None
                            else:
                                # 负数只能是-1，其他负数视为图层名称的一部分
                                result['layer'] = layer_part
                        except ValueError:
                            # 不是有效数字，视为图层名称的一部分
                            result['layer'] = layer_part
                else:
                    result['layer'] = layer_part
                
                # 解析slice名称和其他信息
                if '|' in name_and_context_part:
                    name_parts = name_and_context_part.split('|', 1)
                    result['name'] = name_parts[0]
                    context_part = name_parts[1]
                else:
                    result['name'] = name_and_context_part
                    context_part = ""
                
                # 解析进程、线程、Track信息
                self._parse_process_thread_track(context_part, result)
            else:
                # 格式错误，回退到原来的逻辑
                result['process'] = slice_spec if slice_spec else None
        elif '|' in slice_spec:
            parts = slice_spec.split('|', 1)
            result['name'] = parts[0]
            
            # 检查是否包含#符号（索引信息）
            # 只有当#后面跟有效数字时才视为索引语法
            if '#' in parts[1]:
                # 使用rsplit找到最后一个#，检查后面是否跟有效数字
                context_part, index_part = parts[1].rsplit('#', 1)
                
                # 检查index_part是否为空或包含非数字字符
                if not index_part or not index_part.strip():
                    # #后面没有内容，视为slice名称的一部分
                    context_part = parts[1]
                else:
                    # 检查是否为有效数字
                    index_part = index_part.strip()
                    try:
                        index_value = int(index_part)
                        # 验证索引值的有效性
                        if index_value == -1 or index_value >= 0:
                            result['index'] = index_value
                        else:
                            # 负数只能是-1，其他负数视为slice名称的一部分
                            context_part = parts[1]
                    except ValueError:
                        # 不是有效数字，视为slice名称的一部分
                        context_part = parts[1]
            else:
                context_part = parts[1]
            
            # 解析进程、线程、Track信息（不包含图层，因为图层已经在前面处理了）
            self._parse_process_thread_track(context_part, result)
        
        return result
    
    def _parse_process_thread_track(self, context_part: str, result: dict):
        """
        解析进程、线程、Track信息
        
        Args:
            context_part: 包含进程、线程、Track信息的字符串
            result: 解析结果字典，会被修改
        """
        if '||' in context_part:
            # 检查是否以|||开头（Track名）
            if context_part.startswith('|||'):
                # 包含Track名的情况
                # 格式: |||Track名
                track_name = context_part[3:]  # 移除开头的|||
                result['track'] = track_name if track_name else None
                
                # 没有进程名和线程名
                result['process'] = None
                result['thread'] = None
            elif context_part.startswith('||'):
                # 以||开头，但没有第三个|，这可能是用户想要指定Track名但少写了一个|
                # 格式: ||Track名
                track_name = context_part[2:]  # 移除开头的||
                result['track'] = track_name if track_name else None
                
                # 没有进程名和线程名
                result['process'] = None
                result['thread'] = None
            elif '|||' in context_part:
                # 包含Track名的情况
                # 格式: 进程名||线程名|||Track名
                parts = context_part.split('|||', 1)
                if len(parts) == 2:
                    # 前半部分包含进程名和线程名
                    process_thread_part = parts[0]
                    result['track'] = parts[1] if parts[1] else None
                    
                    # 解析进程名和线程名
                    if '||' in process_thread_part:
                        process_thread_parts = process_thread_part.split('||', 1)
                        result['process'] = process_thread_parts[0] if process_thread_parts[0] else None
                        result['thread'] = process_thread_parts[1] if process_thread_parts[1] else None
                    else:
                        # 只有进程名，没有线程名
                        result['process'] = process_thread_part if process_thread_part else None
                        result['thread'] = None
                else:
                    # 格式错误，回退到原来的逻辑
                    context_parts = context_part.split('||')
                    if len(context_parts) >= 1:
                        result['process'] = context_parts[0] if context_parts[0] else None
                    if len(context_parts) >= 2:
                        result['thread'] = context_parts[1] if context_parts[1] else None
            else:
                # 不包含Track名，只有进程名和线程名
                context_parts = context_part.split('||')
                if len(context_parts) >= 1:
                    result['process'] = context_parts[0] if context_parts[0] else None
                if len(context_parts) >= 2:
                    result['thread'] = context_parts[1] if context_parts[1] else None
        else:
            # 只有进程名，没有线程和Track信息
            result['process'] = context_part if context_part else None
    
    def _build_before_condition(self, slice_obj) -> str:
        """
        构建before条件SQL
        
        Args:
            slice_obj: Slice对象或SliceQueryBuilder对象
            
        Returns:
            str: SQL条件字符串
        """
        if isinstance(slice_obj, Slice):
            # 如果是Slice对象，直接使用其ts值
            return f"slice.ts < {slice_obj.ts}"
        else:
            # 如果是SliceQueryBuilder对象，构建子查询
            boundary_sql = self._build_query_sql(slice_obj)
            return f"slice.ts < (SELECT ts FROM ({boundary_sql}) LIMIT 1)"
    
    def _build_after_condition(self, slice_obj) -> str:
        """
        构建after条件SQL
        
        Args:
            slice_obj: Slice对象或SliceQueryBuilder对象
            
        Returns:
            str: SQL条件字符串
        """
        if isinstance(slice_obj, Slice):
            # 如果是Slice对象，直接使用其ts + dur值
            return f"slice.ts > {slice_obj.ts + slice_obj.dur}"
        else:
            # 如果是SliceQueryBuilder对象，构建子查询
            boundary_sql = self._build_query_sql(slice_obj)
            return f"slice.ts > (SELECT ts + dur FROM ({boundary_sql}) LIMIT 1)"
    
    def _build_between_condition(self, start_slice, end_slice=None) -> str:
        """
        构建between条件SQL
        
        Args:
            start_slice: 开始slice对象或SliceQueryBuilder对象
            end_slice: 结束slice对象或SliceQueryBuilder对象，如果为None则使用start_slice的时间范围
            
        Returns:
            str: SQL条件字符串
        """
        if end_slice is None:
            # 只传入一个slice，使用其时间范围
            if isinstance(start_slice, Slice):
                # 如果是Slice对象，直接使用其时间范围
                start_time = start_slice.ts
                end_time = start_slice.ts + start_slice.dur
                return f"(slice.ts < {end_time} AND slice.ts + slice.dur > {start_time})"
            else:
                # 如果是SliceQueryBuilder对象，构建子查询
                boundary_sql = self._build_query_sql(start_slice)
                return f"""
                (slice.ts < (SELECT ts + dur FROM ({boundary_sql}) LIMIT 1) AND 
                 slice.ts + slice.dur > (SELECT ts FROM ({boundary_sql}) LIMIT 1))
                """
        else:
            # 传入两个slice，使用第一个的开始时间和第二个的结束时间
            if isinstance(start_slice, Slice) and isinstance(end_slice, Slice):
                # 如果都是Slice对象，直接使用其时间值
                start_time = start_slice.ts
                end_time = end_slice.ts + end_slice.dur
                return f"(slice.ts < {end_time} AND slice.ts + slice.dur > {start_time})"
            else:
                # 如果包含SliceQueryBuilder对象，构建子查询
                start_sql = self._build_query_sql(start_slice) if not isinstance(start_slice, Slice) else None
                end_sql = self._build_query_sql(end_slice) if not isinstance(end_slice, Slice) else None
                
                if start_sql and end_sql:
                    return f"""
                    (slice.ts < (SELECT ts + dur FROM ({end_sql}) LIMIT 1) AND 
                     slice.ts + slice.dur > (SELECT ts FROM ({start_sql}) LIMIT 1))
                    """
                elif start_sql:
                    return f"""
                    (slice.ts < {end_slice.ts + end_slice.dur} AND 
                     slice.ts + slice.dur > (SELECT ts FROM ({start_sql}) LIMIT 1))
                    """
                elif end_sql:
                    return f"""
                    (slice.ts < (SELECT ts + dur FROM ({end_sql}) LIMIT 1) AND 
                     slice.ts + slice.dur > {start_slice.ts})
                    """
                else:
                    # 都是Slice对象，但上面的条件没有匹配到，使用直接值
                    start_time = start_slice.ts
                    end_time = end_slice.ts + end_slice.dur
                    return f"(slice.ts < {end_time} AND slice.ts + slice.dur > {start_time})"
    
    def _build_query_sql(self, query: 'SliceQueryBuilder') -> str:
        """
        构建查询的SQL语句
        
        Args:
            query: 查询对象
            
        Returns:
            str: SQL语句
        """
        if not query.sql_parts:
            raise ValueError("Query has no SQL parts")
        
        sql = query.sql_parts[0]
        
        # 添加JOIN
        for join in query.joins:
            sql += f" {join}"
        
        # 添加WHERE条件
        if query.where_conditions:
            sql += " WHERE " + " AND ".join(query.where_conditions)
        
        return sql
    
    def _execute_query(self):
        """内部方法：执行查询并缓存结果"""
        if self._executed:
            return self._results
        
        if not self.sql_parts:
            raise ValueError("No query specified")
        
        sql = self.sql_parts[0]
        for join in self.joins:
            sql += f" {join}"
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        if self.order_by_clause:
            sql += f" ORDER BY {self.order_by_clause}"
        if self.limit_count:
            if hasattr(self, '_offset') and self._offset is not None:
                sql += f" LIMIT {self.limit_count} OFFSET {self._offset}"
            else:
                sql += f" LIMIT {self.limit_count}"
        
        try:
            try:
                from .counter_query_builder import Counter  # 延迟导入，避免循环依赖
            except Exception:
                Counter = None

            result = self.trace_processor.query(sql)
            results = []
            
            for row in result:
                if self.result_type == Slice:
                    enhanced_slice = Slice.from_dict(row)
                    enhanced_slice.set_query_builder(self)
                    results.append(enhanced_slice)
                elif Counter is not None and self.result_type == Counter:
                    results.append(Counter.from_dict(row))
                elif self.result_type == Track:
                    results.append(Track.from_dict(row))
                elif self.result_type == Flow:
                    results.append(Flow.from_dict(row))
                else:
                    results.append(row)
            
            self._results = results
            self._executed = True
            return results
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute query: {e}")
    
    def execute(self) -> Union[Any, List[Any]]:
        """执行查询并返回结果"""
        results = self._execute_query()
        
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            return results
    
    def __iter__(self):
        """支持迭代 - 懒加载"""
        results = self._execute_query()
        return iter(results)
    
    def __getitem__(self, index):
        """支持索引访问 - 懒加载"""
        results = self._execute_query()
        return results[index]
    
    def __len__(self):
        """支持len()函数 - 懒加载"""
        results = self._execute_query()
        return len(results)
    
    def __bool__(self):
        """支持布尔判断 - 懒加载"""
        results = self._execute_query()
        return len(results) > 0
    
    def first(self):
        """获取第一个结果（时间升序）"""
        return self.nth(0)
    
    def last(self):
        """获取最后一个结果（时间升序）"""
        return self.nth(-1)
    
    def all(self):
        """获取全部结果，默认按 ts ASC（时间升序）"""
        if self.current_table in {"slice", "slice_out", "slice_in"} and self.order_by_clause is None:
            self.order_by_clause = f"{self.current_table}.ts ASC"
            self._invalidate_cache()
        return self._execute_query()

    def nth(self, n: int):
        """返回第n个结果（0-based，支持负索引）"""
        results = self.all()
        if not results:
            return None
        if n < 0:
            n = len(results) + n
        if n < 0 or n >= len(results):
            return None
        return results[n]

    def second(self):
        return self.nth(1)

    def third(self):
        return self.nth(2)
    
    def _counter_max(self, field: str = 'value') -> float:
        """
        获取counter指定字段的最大值
        
        Args:
            field: 要计算最大值的字段，默认为'value'
            
        Returns:
            float: 最大值
        """
        
        # 构建MAX查询
        sql = self.sql_parts[0].replace(
            "SELECT \n            counter.*,\n            counter_track.name as track_name,\n            process.name as process_name,\n            process.upid as process_id",
            f"SELECT MAX(counter.{field}) as max_value"
        )
        
        # 添加JOIN
        for join in self.joins:
            sql += f" {join}"
        
        # 添加WHERE条件
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                return getattr(row, 'max_value', None)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to execute max query: {e}")
    
    def _counter_min(self, field: str = 'value') -> float:
        """
        获取counter指定字段的最小值
        
        Args:
            field: 要计算最小值的字段，默认为'value'
            
        Returns:
            float: 最小值
        """
        
        # 构建MIN查询
        sql = self.sql_parts[0].replace(
            "SELECT \n            counter.*,\n            counter_track.name as track_name,\n            process.name as process_name,\n            process.upid as process_id",
            f"SELECT MIN(counter.{field}) as min_value"
        )
        
        # 添加JOIN
        for join in self.joins:
            sql += f" {join}"
        
        # 添加WHERE条件
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                return getattr(row, 'min_value', None)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to execute min query: {e}")
    
    def _counter_avg(self, field: str = 'value') -> float:
        """
        获取counter指定字段的平均值
        
        Args:
            field: 要计算平均值的字段，默认为'value'
            
        Returns:
            float: 平均值
        """
        
        # 构建AVG查询
        sql = self.sql_parts[0].replace(
            "SELECT \n            counter.*,\n            counter_track.name as track_name,\n            process.name as process_name,\n            process.upid as process_id",
            f"SELECT AVG(counter.{field}) as avg_value"
        )
        
        # 添加JOIN
        for join in self.joins:
            sql += f" {join}"
        
        # 添加WHERE条件
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                return getattr(row, 'avg_value', None)
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to execute avg query: {e}")
    
    def cum(self, field: str = 'value') -> dict:
        """
        计算counter指定字段的累积变化值
        分别计算总增量和总减少量
        
        Args:
            field: 要计算累积变化的字段，默认为'value'
            
        Returns:
            dict: 包含'increase'和'decrease'键的字典
                - increase: 总增量（所有增加值的累加）
                - decrease: 总减少量（所有减少值的累加）
        """
        if self.current_table != "counter":
            raise ValueError("cum() method is only available for counter queries")
        
        # 获取所有counter值并按时间戳排序
        try:
            all_counters = self._execute_query()
            if not all_counters or len(all_counters) < 2:
                return {'increase': 0.0, 'decrease': 0.0}
            
            # 按时间戳排序
            sorted_counters = sorted(all_counters, key=lambda x: x.ts)
            
            total_increase = 0.0
            total_decrease = 0.0
            prev_value = None
            
            for counter in sorted_counters:
                current_value = getattr(counter, field, 0.0)
                if prev_value is not None:
                    change = current_value - prev_value
                    if change > 0:
                        # 增加
                        total_increase += change
                    elif change < 0:
                        # 减少
                        total_decrease += abs(change)
                prev_value = current_value
            
            return {'increase': total_increase, 'decrease': total_decrease}
        except Exception as e:
            raise RuntimeError(f"Failed to execute cumulative change query: {e}")
    
    def _resolve_slice_attr_or_arg(self, slice_obj: 'Slice', attr_or_arg: str) -> Any:
        attr_aliases = {
            "duration": "duration_ms",  # 兼容旧接口
            "duration_ns": "dur",
        }
        target = attr_aliases.get(attr_or_arg, attr_or_arg)

        if hasattr(slice_obj, target):
            attr_value = getattr(slice_obj, target)
            if not callable(attr_value):
                return attr_value
        args = slice_obj.get_args() or {}
        return args.get(attr_or_arg)

    def _slice_numeric_values(self, attr_or_arg: str) -> List[float]:
        raw_values = self.to_list(attr_or_arg)
        numeric_values: List[float] = []
        for value in raw_values:
            if value is None:
                continue
            try:
                numeric_values.append(float(value))
            except (TypeError, ValueError):
                continue
        return numeric_values

    def max(self, field: str = None) -> float:
        if self.current_table == "slice":
            target = field or "duration"
            values = [v for v in self.to_list(target) if v is not None]
            return max(values) if values else None
        if self.current_table == "counter":
            return self._counter_max(field or "value")
        raise ValueError("max() method is only available for slice or counter queries")

    def min(self, field: str = None) -> float:
        if self.current_table == "slice":
            target = field or "duration"
            values = [v for v in self.to_list(target) if v is not None]
            return min(values) if values else None
        if self.current_table == "counter":
            return self._counter_min(field or "value")
        raise ValueError("min() method is only available for slice or counter queries")

    def avg(self, field: str = None) -> Optional[float]:
        if self.current_table == "slice":
            target = field or "duration"
            values = self._slice_numeric_values(target)
            if not values:
                return None
            return sum(values) / len(values)
        if self.current_table == "counter":
            return self._counter_avg(field or "value")
        raise ValueError("avg() method is only available for slice or counter queries")

    def sum(self, field: str) -> Optional[float]:
        if self.current_table != "slice":
            raise ValueError("sum() method is only available for slice queries")
        values = self._slice_numeric_values(field)
        if not values:
            return None
        return sum(values)

    def quantile(self, field: str, q: float) -> Optional[float]:
        if self.current_table != "slice":
            raise ValueError("quantile() method is only available for slice queries")
        if q < 0 or q > 1:
            raise ValueError("q must be in range [0, 1]")
        values = self._slice_numeric_values(field)
        if not values:
            return None
        values.sort()
        if len(values) == 1:
            return values[0]
        index = q * (len(values) - 1)
        lo = int(index)
        hi = min(lo + 1, len(values) - 1)
        if lo == hi:
            return values[lo]
        ratio = index - lo
        return values[lo] + (values[hi] - values[lo]) * ratio

    def p90(self, field: str = 'duration') -> Optional[float]:
        return self.quantile(field, 0.9)

    def p95(self, field: str = 'duration') -> Optional[float]:
        return self.quantile(field, 0.95)

    def median(self, field: str = 'duration') -> Optional[float]:
        return self.quantile(field, 0.5)

    def to_list(self, attr_or_arg: str) -> List[Any]:
        if self.current_table != "slice":
            raise ValueError("to_list() method is only available for slice queries")
        slices = self.all()
        return [self._resolve_slice_attr_or_arg(item, attr_or_arg) for item in slices]

    def count(self) -> int:
        if self.current_table == "slice":
            return self._slice_count()
        if self.current_table == "counter":
            return self._counter_count()
        return len(self._execute_query())

    def _slice_count(self) -> int:
        # 使用DISTINCT避免JOIN args时重复计数
        sql = "SELECT COUNT(DISTINCT slice.id) as slice_count FROM slice"
        for join in self.joins:
            sql += f" {join}"
        if self.where_conditions:
            sql += " WHERE " + " AND ".join(self.where_conditions)
        try:
            result = self.trace_processor.query(sql)
            for row in result:
                return getattr(row, 'slice_count', 0)
            return 0
        except Exception as e:
            raise RuntimeError(f"Failed to execute slice count query: {e}")
    
    def _counter_count(self) -> int:
        """
        获取counter查询结果的数量
        
        Returns:
            int: counter数量
        """
        # 构建计数查询，使用与counter查询相同的JOIN结构
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
    
@dataclass
class Slice:
    """表示Perfetto中的一个slice（时间片）"""
    
    id: int
    name: str
    ts: int
    dur: int
    pid: int
    tid: int
    cat: Optional[str]
    track_id: int
    depth: Optional[int] = None
    parent_id: Optional[int] = None
    arg_set_id: Optional[int] = None
    
    # 增强功能的私有属性
    _related_objects: Optional['RelatedObjectsAccessor'] = None
    _query_builder: Optional['SliceQueryBuilder'] = None
    
    def __post_init__(self):
        """初始化后处理"""
        # 将私有属性设置为None，避免dataclass的问题
        if not hasattr(self, '_related_objects'):
            self._related_objects = None
        if not hasattr(self, '_query_builder'):
            self._query_builder = None
    
    @property
    def start_time_ns(self) -> int:
        """开始时间（纳秒）"""
        return self.ts
    
    @property
    def end_time_ns(self) -> int:
        """结束时间（纳秒）"""
        return self.ts + self.dur
    
    @property
    def duration_ns(self) -> int:
        """持续时间（纳秒）"""
        return self.dur
    
    @property
    def start_time_ms(self) -> float:
        """开始时间（毫秒）"""
        return self.ts / 1_000_000
    
    @property
    def end_time_ms(self) -> float:
        """结束时间（毫秒）"""
        return (self.ts + self.dur) / 1_000_000
    
    @property
    def duration_ms(self) -> float:
        """持续时间（毫秒）"""
        return self.dur / 1_000_000
    
    def overlaps_with(self, other: 'Slice') -> bool:
        """检查是否与另一个slice重叠"""
        return not (self.end_time_ms <= other.start_time_ms or other.end_time_ms <= self.start_time_ms)
    
    def contains_timestamp(self, timestamp_ms: float) -> bool:
        """检查是否包含指定时间戳"""
        return self.start_time_ms <= timestamp_ms <= self.end_time_ms
    
    def contains(self, timestamp_ns: int) -> bool:
        """检查是否包含指定时间戳（纳秒）"""
        return self.ts <= timestamp_ns < self.ts + self.dur
    
    def set_query_builder(self, query_builder: 'SliceQueryBuilder'):
        """设置查询构建器"""
        self._query_builder = query_builder
    
    @property
    def related(self) -> 'RelatedObjectsAccessor':
        """获取关联对象访问器"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot access related objects.")
        
        if self._related_objects is None:
            from .slice_query_builder import RelatedObjectsAccessor
            self._related_objects = RelatedObjectsAccessor(self._query_builder, self)
        
        return self._related_objects
    
    @property
    def process(self):
        """直接访问process属性"""
        return self.related.process
    
    @property
    def thread(self):
        """直接访问thread属性"""
        return self.related.thread
    
    @property
    def track(self):
        """直接访问track属性"""
        return self.related.track
    
    def get_arg(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        args_dict = self.get_args()
        if args_dict is None:
            return default
        return args_dict.get(key, default)

    def arg(self, key: str, default: Any = None) -> Any:
        """OpenSpec别名：s.arg(key)"""
        return self.get_arg(key, default)
    
    def input_id(self, default: str = None) -> Optional[str]:
        """
        从 slice name 中提取 id=0x1dc76a4d 格式的 ID 值
        
        Args:
            default: 如果未找到 ID 时返回的默认值
            
        Returns:
            str: 提取的 ID 值（如 "0x1dc76a4d"），如果未找到则返回 default
            
        Example:
            slice.name = "Some operation id=0x1dc76a4d"
            id_value = slice.input_id()  # 返回 "0x1dc76a4d"
        """
        # 匹配 id=0x 开头的十六进制值
        pattern = r'id=(0x[0-9a-fA-F]+)'
        match = re.search(pattern, self.name)
        
        if match:
            return match.group(1)
        return default
    
    def frame_id(self, default: int = None) -> Optional[int]:
        """
        从 slice name 中提取 Choreographer#doFrame 787448 格式的帧号值
        
        Args:
            default: 如果未找到帧号时返回的默认值
            
        Returns:
            int: 提取的帧号值（如 787448），如果未找到则返回 default
            
        Example:
            slice.name = "Choreographer#doFrame 787448"
            frame_number = slice.frame_id()  # 返回 787448
        """
        # 匹配 Choreographer#doFrame 后面的数字
        pattern = r'Choreographer#doFrame\s+(\d+)'
        match = re.search(pattern, self.name)
        
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return default
        return default
    
    def get_process_name(self) -> str:
        """获取进程名"""
        if self._query_builder is None:
            return ""
        
        try:
            # 首先尝试通过process_track查询进程信息
            result = self._query_builder.trace_processor.query(f"""
                SELECT p.name 
                FROM track t
                JOIN process_track pt ON t.id = pt.id
                JOIN process p ON pt.upid = p.upid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    if row.name:
                        return row.name
            
            # 如果没有找到，尝试通过thread_track查询进程信息
            result = self._query_builder.trace_processor.query(f"""
                SELECT p.name 
                FROM track t
                JOIN thread_track tt ON t.id = tt.id
                JOIN thread th ON tt.utid = th.utid
                JOIN process p ON th.upid = p.upid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    if row.name:
                        return row.name
        except Exception:
            pass
        return ""
    
    def get_thread_name(self) -> str:
        """获取线程名"""
        if self._query_builder is None:
            return ""
        
        try:
            # 通过track_id查询线程信息
            result = self._query_builder.trace_processor.query(f"""
                SELECT th.name 
                FROM track t
                JOIN thread_track tt ON t.id = tt.id
                JOIN thread th ON tt.utid = th.utid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    # 如果有名称且不是'None'字符串，返回名称；否则返回空字符串
                    if row.name and row.name != 'None':
                        return row.name
        except Exception:
            pass
        return ""
    
    def get_track_name(self) -> str:
        """获取 track 名"""
        if self._query_builder is None:
            return ""
        
        try:
            # 查询 track 信息
            result = self._query_builder.trace_processor.query(
                f"SELECT name FROM track WHERE id = {self.track_id}"
            )
            if result:
                for row in result:
                    # 如果有名称且不是'None'字符串，返回名称；否则返回空字符串
                    if row.name and row.name != 'None':
                        return row.name
        except Exception:
            pass
        return ""
    
    def get_upid(self) -> Optional[int]:
        """获取进程的upid"""
        if self._query_builder is None:
            return None
        
        try:
            # 首先尝试通过process_track查询upid
            result = self._query_builder.trace_processor.query(f"""
                SELECT pt.upid 
                FROM track t
                JOIN process_track pt ON t.id = pt.id
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    if row.upid is not None:
                        return row.upid
            
            # 如果没有找到，尝试通过thread_track查询upid
            result = self._query_builder.trace_processor.query(f"""
                SELECT th.upid 
                FROM track t
                JOIN thread_track tt ON t.id = tt.id
                JOIN thread th ON tt.utid = th.utid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    if row.upid is not None:
                        return row.upid
        except Exception:
            pass
        return None
    
    def get_utid(self) -> Optional[int]:
        """获取线程的utid"""
        if self._query_builder is None:
            return None
        
        try:
            # 通过track_id查询utid
            result = self._query_builder.trace_processor.query(f"""
                SELECT tt.utid 
                FROM track t
                JOIN thread_track tt ON t.id = tt.id
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    return row.utid
        except Exception:
            pass
        return None
    
    def get_pid(self) -> Optional[int]:
        """获取进程的pid"""
        if self._query_builder is None:
            return None
        
        try:
            # 首先尝试通过process_track查询pid
            result = self._query_builder.trace_processor.query(f"""
                SELECT p.pid 
                FROM track t
                JOIN process_track pt ON t.id = pt.id
                JOIN process p ON pt.upid = p.upid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    if row.pid is not None:
                        return row.pid
            
            # 如果没有找到，尝试通过thread_track查询pid
            result = self._query_builder.trace_processor.query(f"""
                SELECT p.pid 
                FROM track t
                JOIN thread_track tt ON t.id = tt.id
                JOIN thread th ON tt.utid = th.utid
                JOIN process p ON th.upid = p.upid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    if row.pid is not None:
                        return row.pid
        except Exception:
            pass
        return None
    
    def get_tid(self) -> Optional[int]:
        """获取线程的tid"""
        if self._query_builder is None:
            return None
        
        try:
            # 通过track_id查询tid
            result = self._query_builder.trace_processor.query(f"""
                SELECT th.tid 
                FROM track t
                JOIN thread_track tt ON t.id = tt.id
                JOIN thread th ON tt.utid = th.utid
                WHERE t.id = {self.track_id}
            """)
            if result:
                for row in result:
                    return row.tid
        except Exception:
            pass
        return None
    
    def get_args(self) -> Optional[Dict[str, Any]]:
        """获取slice的args参数"""
        if self._query_builder is None:
            return None
        
        try:
            # 通过arg_set_id查询args表
            result = self._query_builder.trace_processor.query(f"""
                SELECT key, value_type, int_value, string_value, real_value, display_value
                FROM args 
                WHERE arg_set_id = {self.arg_set_id}
            """)
            
            args_dict = {}
            for row in result:
                key = row.key
                value_type = row.value_type
                
                # 根据value_type获取正确的值
                if value_type == 'int':
                    value = row.int_value
                elif value_type == 'string':
                    value = row.string_value
                elif value_type == 'real':
                    value = row.real_value
                else:
                    value = row.display_value
                
                args_dict[key] = value
            
            return args_dict if args_dict else None
        except Exception:
            pass
        return None
    
    def args_dict(self) -> Optional[Dict[str, Any]]:
        """获取slice的args参数字典"""
        return self.get_args()
    
    def args(self, key: Optional[str] = None, value: Any = None) -> Any:
        """
        获取slice的args参数或进行args过滤
        
        Args:
            key: 如果提供，返回指定key的值；如果不提供，返回完整的args字典
            value: 如果提供，则进行args过滤，返回匹配的slice列表
            
        Returns:
            如果key为None，返回完整的args字典
            如果只有key，返回指定key的值
            如果key和value都有，返回匹配的slice列表
            
        Examples:
            # 获取完整的args字典
            args_dict = slice.args()
            
            # 获取指定key的值
            value = slice.args("key_name")
            
            # 使用args进行过滤
            filtered_slices = slice.args("key_name", "value_pattern")
        """
        # 如果提供了value，进行过滤
        if value is not None:
            if self._query_builder is None:
                raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform args filtering.")
            
            # 延迟导入避免循环导入
            from .slice_query_builder import SliceQueryBuilder
            
            # 创建新的查询构建器进行args过滤
            new_builder = SliceQueryBuilder(self._query_builder.trace_processor)
            new_builder.current_table = "slice"
            new_builder.result_type = Slice
            new_builder.sql_parts = ["SELECT slice.* FROM slice"]
            
            # 添加args过滤条件
            new_builder.joins.append("JOIN args ON slice.arg_set_id = args.arg_set_id")
            
            if isinstance(value, str):
                new_builder.where_conditions.append(f"args.key = '{key}' AND args.string_value LIKE '%{value}%'")
            else:
                new_builder.where_conditions.append(f"args.key = '{key}' AND args.int_value = {value}")
            
            # 执行查询并返回结果
            results = new_builder._execute_query()
            return results if results else []
        
        # 如果没有提供value，按原来的逻辑处理
        args_dict = self.get_args()
        if args_dict is None:
            return None
        
        if key is None:
            # 返回完整的args字典
            return args_dict
        else:
            # 返回指定key的值
            return args_dict.get(key, None)
    
    def args_filter(self, **kwargs) -> List['Slice']:
        """基于args进行过滤查询，返回匹配的slice列表"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform args filtering.")
        
        # 延迟导入避免循环导入
        from .slice_query_builder import SliceQueryBuilder
        
        # 创建新的查询构建器进行args过滤
        new_builder = SliceQueryBuilder(self._query_builder.trace_processor)
        new_builder.current_table = "slice"
        new_builder.result_type = Slice
        
        # 添加当前slice的ID条件
        new_builder.sql_parts = ["SELECT slice.* FROM slice"]
        new_builder.where_conditions.append(f"slice.id = {self.id}")
        
        # 添加args过滤条件
        new_builder.joins.append("JOIN args ON slice.arg_set_id = args.arg_set_id")
        for key, value in kwargs.items():
            # 将下划线替换为空格，因为args的key通常包含空格
            arg_key = key.replace('_', ' ')
            if isinstance(value, str):
                new_builder.where_conditions.append(f"args.key = '{arg_key}' AND args.string_value LIKE '{value}'")
            else:
                new_builder.where_conditions.append(f"args.key = '{arg_key}' AND args.int_value = {value}")
        
        # 执行查询并返回结果
        results = new_builder._execute_query()
        return results if results else []
    
    def child(self, level: int = 1, **kwargs):
        """查找子节点，支持链式调用"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform child query.")
        
        # 创建新的查询构建器，基于当前 slice 查找子节点
        new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
        new_builder.current_table = "slice"
        new_builder.result_type = self._query_builder.result_type
        new_builder.sql_parts = ["SELECT child_slice.* FROM slice"]
        new_builder.where_conditions = [f"slice.id = {self.id}"]
        
        # 调用 child 方法
        return new_builder.child(level, **kwargs)

    def descendants(self, **kwargs):
        """查找所有子孙节点，支持链式调用"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform descendants query.")
        new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
        new_builder.slice(id=self.id)
        return new_builder.descendants(**kwargs)
    
    def parent(self, level: int = 1, **kwargs):
        """查找父节点，支持链式调用"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform parent query.")
        
        # 特殊处理 level=-1 的情况
        if level == -1:
            # 当depth为0时，返回slice自己
            if self.depth == 0:
                # 创建一个返回自己的查询构建器
                new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
                new_builder.current_table = "slice"
                new_builder.result_type = self._query_builder.result_type
                new_builder.sql_parts = ["SELECT slice.* FROM slice"]
                new_builder.where_conditions = [f"slice.id = {self.id}"]
                
                # 添加额外的过滤条件
                for key, value in kwargs.items():
                    if isinstance(value, str):
                        new_builder.where_conditions.append(f"slice.{key} LIKE '{value}'")
                    else:
                        new_builder.where_conditions.append(f"slice.{key} = {value}")
                
                return new_builder
            else:
                # 当depth不为0时，查找父节点
                if self.parent_id is None:
                    # 没有父节点，返回空结果
                    new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
                    new_builder.current_table = "slice"
                    new_builder.result_type = self._query_builder.result_type
                    new_builder.sql_parts = ["SELECT slice.* FROM slice"]
                    new_builder.where_conditions = ["1 = 0"]  # 永远不匹配的条件
                    return new_builder
                else:
                    # 有父节点，查询父节点
                    new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
                    new_builder.current_table = "slice"
                    new_builder.result_type = self._query_builder.result_type
                    # 复制原始的SQL parts，确保包含process.pid和thread.tid
                    new_builder.sql_parts = self._query_builder.sql_parts.copy()
                    new_builder.where_conditions = [f"slice.id = {self.parent_id}"]
                    
                    # 复制原始的JOIN信息，确保能获取process和thread信息
                    if hasattr(self._query_builder, 'joins'):
                        new_builder.joins = self._query_builder.joins.copy()
                    
                    # 添加额外的过滤条件
                    for key, value in kwargs.items():
                        if isinstance(value, str):
                            new_builder.where_conditions.append(f"slice.{key} LIKE '{value}'")
                        else:
                            new_builder.where_conditions.append(f"slice.{key} = {value}")
                    
                    return new_builder
        
        # 其他level值的处理（保持原有逻辑）
        new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
        new_builder.current_table = "slice"
        new_builder.result_type = self._query_builder.result_type
        new_builder.sql_parts = ["SELECT slice.* FROM slice"]
        new_builder.where_conditions = [f"slice.id = {self.parent_id}"]  # 直接查询父节点
        
        # 添加额外的过滤条件
        for key, value in kwargs.items():
            if isinstance(value, str):
                new_builder.where_conditions.append(f"slice.{key} LIKE '{value}'")
            else:
                new_builder.where_conditions.append(f"slice.{key} = {value}")
        
        return new_builder
    
    def siblings(self, **kwargs):
        """查找兄弟节点，支持链式调用"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform siblings query.")
        
        # 创建新的查询构建器，基于当前 slice 查找兄弟节点
        new_builder = self._query_builder.__class__(self._query_builder.trace_processor)
        new_builder.current_table = "slice"
        new_builder.result_type = self._query_builder.result_type
        new_builder.sql_parts = ["SELECT sibling_slice.* FROM slice"]
        new_builder.where_conditions = [f"slice.id = {self.id}"]
        
        # 调用 siblings 方法
        return new_builder.siblings(**kwargs)
    
    def flow_out(self, **kwargs):
        """查找当前slice作为source时的flow对端（FlowLink）"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform flow_out query.")
        builder = FlowLinkQueryBuilder(self._query_builder.trace_processor, self, "out")
        if "name" in kwargs:
            builder.name(kwargs["name"])
        if "args" in kwargs and isinstance(kwargs["args"], dict):
            for key, value in kwargs["args"].items():
                builder.arg(key).compare("==", value)
        return builder
    
    def flow_in(self, **kwargs):
        """查找当前slice作为sink时的flow对端（FlowLink）"""
        if self._query_builder is None:
            raise RuntimeError("SliceQueryBuilder not set for Slice. Cannot perform flow_in query.")
        builder = FlowLinkQueryBuilder(self._query_builder.trace_processor, self, "in")
        if "name" in kwargs:
            builder.name(kwargs["name"])
        if "args" in kwargs and isinstance(kwargs["args"], dict):
            for key, value in kwargs["args"].items():
                builder.arg(key).compare("==", value)
        return builder
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'ts': self.ts,
            'dur': self.dur,
            'pid': self.pid,
            'tid': self.tid,
            'cat': self.cat,
            'track_id': self.track_id,
            'depth': self.depth,
            'parent_id': self.parent_id,
            'arg_set_id': self.arg_set_id
        }
    
    @classmethod
    def from_dict(cls, data) -> 'Slice':
        """从字典或Row对象创建Slice实例"""
        # 处理perfetto的Row对象（支持属性访问）
        if hasattr(data, 'id'): # Check if it's a Row object or similar
            return cls(
                id=getattr(data, 'id', 0),
                name=getattr(data, 'name', ''),
                ts=getattr(data, 'ts', 0),
                dur=getattr(data, 'dur', 0),
                pid=getattr(data, 'pid', 0),
                tid=getattr(data, 'tid', 0),
                cat=getattr(data, 'cat', ''),
                track_id=getattr(data, 'track_id', 0),
                depth=getattr(data, 'depth', None),
                parent_id=getattr(data, 'parent_id', None),
                arg_set_id=getattr(data, 'arg_set_id', None)
            )
        else:
            # 如果是普通字典
            return cls(
                id=data['id'],
                name=data['name'],
                ts=data['ts'],
                dur=data['dur'],
                pid=data.get('pid'),
                tid=data.get('tid'),
                cat=data['cat'],
                track_id=data['track_id'],
                depth=data.get('depth'),
                parent_id=data.get('parent_id'),
                arg_set_id=data.get('arg_set_id')
            )
    
    def __str__(self) -> str:
        """用户友好的字符串表示，包含process、thread、track信息"""
        # 获取进程名、线程名、track名、pid和tid
        process_name = self.get_process_name()
        thread_name = self.get_thread_name()
        track_name = self.get_track_name()
        pid = self.get_pid()
        tid = self.get_tid()
        
        # 构建信息字符串，只显示非空字符串和非None值
        info_parts = []
        if process_name:  # 空字符串会被过滤掉
            info_parts.append(f"process='{process_name}'")
        if thread_name:  # 空字符串会被过滤掉
            info_parts.append(f"thread='{thread_name}'")
        if track_name:  # 空字符串会被过滤掉
            info_parts.append(f"track='{track_name}'")
        if pid is not None:  # None值会被过滤掉
            info_parts.append(f"pid={pid}")
        if tid is not None:  # None值会被过滤掉
            info_parts.append(f"tid={tid}")
        
        info_str = f", {', '.join(info_parts)}" if info_parts else ""
        
        return f"Slice(id={self.id}, name='{self.name}', ts={self.start_time_ms:.2f}ms, duration={self.duration_ms:.2f}ms{info_str})"
    
    def __repr__(self) -> str:
        """开发者友好的字符串表示，包含调试信息"""
        # 获取进程名、线程名、track名、pid和tid
        process_name = self.get_process_name()
        thread_name = self.get_thread_name()
        track_name = self.get_track_name()
        pid = self.get_pid()
        tid = self.get_tid()
        
        # 构建信息字符串，只显示非空字符串和非None值
        info_parts = []
        if process_name:  # 空字符串会被过滤掉
            info_parts.append(f"process='{process_name}'")
        if thread_name:  # 空字符串会被过滤掉
            info_parts.append(f"thread='{thread_name}'")
        if track_name:  # 空字符串会被过滤掉
            info_parts.append(f"track='{track_name}'")
        if pid is not None:  # None值会被过滤掉
            info_parts.append(f"pid={pid}")
        if tid is not None:  # None值会被过滤掉
            info_parts.append(f"tid={tid}")
        
        info_str = f", {', '.join(info_parts)}" if info_parts else ""
        
        return f"Slice(id={self.id}, name='{self.name}', ts={self.ts}, dur={self.dur}, cat='{self.cat}', track_id={self.track_id}, depth={self.depth}, parent_id={self.parent_id}{info_str})"
