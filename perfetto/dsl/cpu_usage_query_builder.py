#!/usr/bin/env python3
"""
CPU 使用率查询构建器（优化版）
"""

from typing import List, Optional, Union, Dict
from dataclasses import dataclass
from .slice_query_builder import Slice


@dataclass
class CpuUsageData:
    """CPU 使用率数据"""
    process_name: Optional[str]
    thread_name: Optional[str]
    thread_id: int
    total_runtime_ns: int
    total_duration_ns: int
    usage_percentage: float
    cpu_count: int

    @property
    def total_runtime_ms(self) -> float:
        return self.total_runtime_ns / 1_000_000

    @property
    def total_duration_ms(self) -> float:
        return self.total_duration_ns / 1_000_000

    def __str__(self) -> str:
        return (f"CpuUsage(process='{self.process_name}', "
                f"thread='{self.thread_name}', "
                f"thread_id={self.thread_id}, "
                f"usage={self.usage_percentage:.6f} ({self.usage_percentage*100:.2f}%), "
                f"runtime={self.total_runtime_ms:.2f}ms)")

    def __repr__(self) -> str:
        return (f"CpuUsageData(process_name='{self.process_name}', "
                f"thread_name='{self.thread_name}', "
                f"thread_id={self.thread_id}, "
                f"total_runtime_ns={self.total_runtime_ns}, "
                f"total_duration_ns={self.total_duration_ns}, "
                f"usage_percentage={self.usage_percentage:.2f}, "
                f"cpu_count={self.cpu_count})")


class CpuUsageQueryBuilder:
    """CPU 使用率查询构建器，支持链式调用"""

    def __init__(self, trace_processor, **kwargs):
        self.trace_processor = trace_processor
        self.where_conditions: List[str] = []
        self.time_conditions: List[str] = []
        self._executed = False
        self._results: List[CpuUsageData] = []

        # 初始化标志
        self._return_process_dict = False
        self._return_thread_dict = False
        self._return_cpu_dict = False
        self._return_overall_usage = False

        # 可选过滤条件
        for key, func in (('process_name', self.process),
                          ('thread_name', self.thread),
                          ('cpu_id', self.cpu)):
            if key in kwargs:
                func(kwargs[key])

    # ======== 辅助函数 ========

    @staticmethod
    def _calc_usage(total_runtime_ns: int, total_duration_ns: int, cpu_count: int) -> float:
        """CPU使用率计算（返回小数，1.0=100%）"""
        if total_duration_ns <= 0 or cpu_count <= 0:
            return 0.0
        return total_runtime_ns / (cpu_count * total_duration_ns)
    
    def _calc_filtered_usage(self, total_runtime_ns: int) -> float:
        """计算过滤后的CPU使用率（返回小数，1.0=100%）"""
        # 获取原始的时间范围和CPU数量（不过滤）
        sql = f"""
        WITH time_range AS (
            SELECT MIN(ts) AS min_ts, MAX(ts + dur) AS max_ts,
                   COUNT(DISTINCT ucpu) AS cpu_count
            FROM sched
        )
        SELECT min_ts, max_ts, cpu_count FROM time_range
        """
        result = self._query(sql)
        if not result:
            return 0.0
        
        # 获取第一行结果
        row = next(iter(result), None)
        if not row:
            return 0.0
            
        total_duration_ns = row.max_ts - row.min_ts
        cpu_count = row.cpu_count
        
        # 返回小数，与_calc_usage保持一致
        return total_runtime_ns / (cpu_count * total_duration_ns)

    def _build_base_sql(self) -> str:
        """统一构建 SQL 前置模板"""
        conditions = self.where_conditions + self.time_conditions
        conditions.append("NOT (process.pid = 0 AND thread.tid = 0)")
        where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""

        return f"""
        WITH filtered_sched AS (
            SELECT sched.*, process.name AS process_name, thread.name AS thread_name
            FROM sched
            JOIN thread ON sched.utid = thread.utid
            JOIN process ON thread.upid = process.upid
            {where_clause}
        ),
        time_range AS (
            SELECT MIN(ts) AS min_ts, MAX(ts + dur) AS max_ts,
                   COUNT(DISTINCT ucpu) AS cpu_count
            FROM filtered_sched
        )
        """

    def _query(self, sql: str):
        """安全执行 SQL"""
        try:
            return self.trace_processor.query(sql)
        except Exception as e:
            print(f"[SQL 查询错误]: {e}\nSQL 片段:\n{sql[:300]}...")
            return []

    # ======== 条件构建 ========

    def process(self, name: Union[str, List[str], None] = None) -> 'CpuUsageQueryBuilder':
        if name is None:
            # 没有参数时，返回所有进程的字典格式
            self._return_process_dict = True
        else:
            # 有参数时，过滤特定进程，返回整体使用率
            names = [name] if isinstance(name, str) else name
            cond = " OR ".join(f"process.name LIKE '{n}'" for n in names)
            self.where_conditions.append(f"({cond})")
        return self

    def thread(self, name: Union[str, List[str], None] = None) -> 'CpuUsageQueryBuilder':
        if name is None:
            # 没有参数时，返回所有线程的字典格式
            self._return_thread_dict = True
        else:
            # 有参数时，过滤特定线程，返回整体使用率
            names = [name] if isinstance(name, str) else name
            cond = " OR ".join(f"thread.name LIKE '{n}'" for n in names)
            self.where_conditions.append(f"({cond})")
        return self

    def cpu(self, cpu_id: Optional[int] = None) -> 'CpuUsageQueryBuilder':
        if cpu_id is None:
            self._return_cpu_dict = True
        else:
            self.where_conditions.append(f"sched.ucpu = {cpu_id}")
        return self

    def before(self, slice_obj) -> 'CpuUsageQueryBuilder':
        if isinstance(slice_obj, str):
            slice_obj = self._create_slice_from_spec(slice_obj)
        self.time_conditions.append(f"sched.ts < {slice_obj.ts}")
        return self

    def after(self, slice_obj) -> 'CpuUsageQueryBuilder':
        if isinstance(slice_obj, str):
            slice_obj = self._create_slice_from_spec(slice_obj)
        self.time_conditions.append(f"sched.ts > {slice_obj.ts + slice_obj.dur}")
        return self

    def between(self, start_slice, end_slice: Optional[Slice] = None) -> 'CpuUsageQueryBuilder':
        if isinstance(start_slice, str):
            start_slice = self._create_slice_from_spec(start_slice)
        if end_slice and isinstance(end_slice, str):
            end_slice = self._create_slice_from_spec(end_slice)
        
        start_time = start_slice.ts
        end_time = (end_slice.ts + end_slice.dur) if end_slice else (start_slice.ts + start_slice.dur)
        self.time_conditions += [f"sched.ts >= {start_time}", f"sched.ts <= {end_time}"]
        return self

    # ======== 通用聚合查询 ========

    def _get_grouped_usage(self, group_by: List[str]) -> Dict:
        group_clause = ", ".join(group_by)
        sql = f"""
        {self._build_base_sql()}
        SELECT {group_clause},
               SUM(fs.dur) AS total_runtime_ns,
               (tr.max_ts - tr.min_ts) AS total_duration_ns,
               tr.cpu_count
        FROM filtered_sched fs
        CROSS JOIN time_range tr
        GROUP BY {group_clause}, tr.max_ts, tr.min_ts, tr.cpu_count
        ORDER BY total_runtime_ns DESC
        """
        result = self._query(sql)
        data = {}

        for row in result:
            fields = {k: getattr(row, k, '') for k in group_by}
            runtime = getattr(row, 'total_runtime_ns', 0)
            dur = getattr(row, 'total_duration_ns', 0)
            cpu_cnt = getattr(row, 'cpu_count', 1)
            usage = self._calc_usage(runtime, dur, cpu_cnt)

            d = data
            for k in group_by[:-1]:
                d = d.setdefault(fields[k], {})
            d[fields[group_by[-1]]] = usage

        return data

    # ======== 主查询 ========

    def _build_query(self) -> str:
        return f"""
        {self._build_base_sql()}
        SELECT fs.process_name, fs.thread_name, fs.utid AS thread_id,
               SUM(fs.dur) AS total_runtime_ns,
               (tr.max_ts - tr.min_ts) AS total_duration_ns,
               tr.cpu_count
        FROM filtered_sched fs
        CROSS JOIN time_range tr
        GROUP BY fs.process_name, fs.thread_name, fs.utid, tr.max_ts, tr.min_ts, tr.cpu_count
        ORDER BY total_runtime_ns DESC
        """

    def _execute_query(self) -> List[CpuUsageData]:
        if self._executed:
            return self._results
        sql = self._build_query()
        result = self._query(sql)
        self._results = [
            CpuUsageData(
                process_name=r.process_name,
                thread_name=r.thread_name,
                thread_id=r.thread_id,
                total_runtime_ns=r.total_runtime_ns,
                total_duration_ns=r.total_duration_ns,
                usage_percentage=self._calc_usage(r.total_runtime_ns, r.total_duration_ns, r.cpu_count),
                cpu_count=r.cpu_count
            ) for r in result
        ]
        self._executed = True
        return self._results

    # ======== 统计输出 ========

    def total_usage(self) -> float:
        results = self._execute_query()
        if not results:
            return 0.0
        total_runtime_ns = sum(r.total_runtime_ns for r in results)
        sample = results[0]
        
        # 如果有过滤条件，需要重新计算总时长和CPU数量
        if len(self.where_conditions) > 0:
            # 使用整个trace的时间范围重新计算
            return self._calc_filtered_usage(total_runtime_ns)
        else:
            return self._calc_usage(total_runtime_ns, sample.total_duration_ns, sample.cpu_count)

    # ======== 接口实现 ========

    def __str__(self) -> str:
        """字符串表示 - 懒加载，根据查询类型返回不同格式"""
        import json
        
        # 检查是否有过滤条件（where_conditions）
        has_filters = len(self.where_conditions) > 0
        
        # 1. 如果有过滤条件，返回过滤后的整体CPU使用率
        if has_filters:
            filtered_usage = self.total_usage()
            return f"{filtered_usage:.6f}"
        
        # 2. 如果没有任何特殊标志，返回整体CPU使用率
        if not any([self._return_process_dict, self._return_thread_dict, self._return_cpu_dict]):
            overall_usage = self.total_usage()
            return f"{overall_usage:.6f}"
        
        # 3. 如果设置了 process 标志，返回单层进程字典
        if self._return_process_dict and not self._return_thread_dict:
            process_dict = self._get_process_usage_dict()
            return json.dumps(process_dict, indent=2, ensure_ascii=False)
        
        # 4. 如果设置了 thread 标志，返回单层线程字典
        if self._return_thread_dict and not self._return_process_dict:
            thread_dict = self._get_thread_usage_dict()
            return json.dumps(thread_dict, indent=2, ensure_ascii=False)
        
        # 5. 如果同时设置了 process 和 thread，返回嵌套字典结构（JSON美化）
        if self._return_process_dict and self._return_thread_dict:
            nested_dict = self._get_nested_usage_dict()
            return json.dumps(nested_dict, indent=2, ensure_ascii=False)
        
        # 6. 否则返回数据列表
        results = self._execute_query()
        if len(results) == 0:
            return "CpuUsageQueryBuilder: No results"
        else:
            # 直接输出所有结果的字符串表示
            result_strings = [str(result) for result in results]
            return '\n'.join(result_strings)

    def __len__(self) -> int:
        if self._return_cpu_dict:
            return len(self._get_grouped_usage(["ucpu"]))
        if self._return_thread_dict and self._return_process_dict:
            return len(self._get_grouped_usage(["process_name", "thread_name"]))
        if self._return_thread_dict:
            return len(self._get_grouped_usage(["thread_name"]))
        if self._return_process_dict:
            return len(self._get_grouped_usage(["process_name"]))
        return 0

    def __getitem__(self, key):
        data = None
        if self._return_cpu_dict:
            data = self._get_grouped_usage(["ucpu"])
            key = f"CPU {key}" if isinstance(key, int) else key
        elif self._return_thread_dict and self._return_process_dict:
            data = self._get_grouped_usage(["process_name", "thread_name"])
        elif self._return_thread_dict:
            data = self._get_grouped_usage(["thread_name"])
        elif self._return_process_dict:
            data = self._get_grouped_usage(["process_name"])
        if data and key in data:
            return data[key]
        raise KeyError(key)

    def items(self):
        if self._return_cpu_dict:
            return self._get_grouped_usage(["ucpu"]).items()
        if self._return_thread_dict and self._return_process_dict:
            return self._get_grouped_usage(["process_name", "thread_name"]).items()
        if self._return_thread_dict:
            return self._get_grouped_usage(["thread_name"]).items()
        if self._return_process_dict:
            return self._get_grouped_usage(["process_name"]).items()
        return []

    def __repr__(self) -> str:
        return f"{self.total_usage():.4f}%"
    
    def __iter__(self):
        """支持迭代"""
        return iter(self._execute_query())
    
    def get_stats(self) -> Dict:
        """获取统计信息（JSON格式）"""
        has_cpu, has_proc, has_thread = (
            self._return_cpu_dict, self._return_process_dict, self._return_thread_dict
        )

        if has_cpu and has_proc and has_thread:
            return self._get_grouped_usage(["ucpu", "process_name", "thread_name"])
        if has_cpu and has_proc:
            return self._get_grouped_usage(["ucpu", "process_name"])
        if has_cpu and has_thread:
            return self._get_grouped_usage(["ucpu", "thread_name"])
        if has_cpu:
            return self._get_grouped_usage(["ucpu"])
        if has_proc and has_thread:
            return self._get_grouped_usage(["process_name", "thread_name"])
        if has_thread:
            return self._get_grouped_usage(["thread_name"])
        if has_proc:
            return self._get_grouped_usage(["process_name"])

        return {}
    
    def get_stats_json(self) -> str:
        """获取统计信息（JSON字符串格式）"""
        import json
        return json.dumps(self.get_stats(), indent=2, ensure_ascii=False)
    
    def _get_process_usage_dict(self) -> Dict[str, float]:
        """获取单层进程字典格式的CPU使用率数据
        
        Returns:
            Dict[str, float]: key为进程名，值为CPU使用率(1.0=100%)，按使用率从高到低排序
        """
        results = self._execute_query()
        process_dict = {}
        
        for result in results:
            process_name = result.process_name or "unknown"
            usage_ratio = result.usage_percentage / 100.0  # 百分比转换为比例 (1.0 = 100%)
            
            if process_name in process_dict:
                process_dict[process_name] += usage_ratio
            else:
                process_dict[process_name] = usage_ratio
        
        # 按使用率从高到低排序
        sorted_process_dict = dict(sorted(process_dict.items(), key=lambda x: x[1], reverse=True))
        return sorted_process_dict
    
    def _get_thread_usage_dict(self) -> Dict[str, float]:
        """获取单层线程字典格式的CPU使用率数据
        
        Returns:
            Dict[str, float]: key为线程名，值为CPU使用率(1.0=100%)，按使用率从高到低排序
        """
        results = self._execute_query()
        thread_dict = {}
        
        for result in results:
            thread_name = result.thread_name or "unknown"
            usage_ratio = result.usage_percentage / 100.0  # 百分比转换为比例 (1.0 = 100%)
            
            if thread_name in thread_dict:
                thread_dict[thread_name] += usage_ratio
            else:
                thread_dict[thread_name] = usage_ratio
        
        # 按使用率从高到低排序
        sorted_thread_dict = dict(sorted(thread_dict.items(), key=lambda x: x[1], reverse=True))
        return sorted_thread_dict

    def _get_nested_usage_dict(self) -> Dict[str, Dict[str, float]]:
        """获取嵌套字典格式的CPU使用率数据
        
        Returns:
            Dict[str, Dict[str, float]]: 外层key为进程名，内层key为线程名，值为CPU使用率(1.0=100%)，按名字增序排序
        """
        results = self._execute_query()
        nested_dict = {}
        
        for result in results:
            process_name = result.process_name or "unknown"
            thread_name = result.thread_name or "unknown"
            usage_ratio = result.usage_percentage / 100.0  # 百分比转换为比例 (1.0 = 100%)
            
            if process_name not in nested_dict:
                nested_dict[process_name] = {}
            
            nested_dict[process_name][thread_name] = usage_ratio
        
        # 按进程名和线程名增序排序
        sorted_nested_dict = {}
        for process_name in sorted(nested_dict.keys()):
            sorted_nested_dict[process_name] = dict(sorted(nested_dict[process_name].items()))
        
        return sorted_nested_dict

    def _create_slice_from_spec(self, slice_spec: str) -> Slice:
        """从slice规格字符串创建Slice对象"""
        from .slice_query_builder import SliceQueryBuilder
        
        # 创建SliceQueryBuilder来查找slice
        slice_builder = SliceQueryBuilder(self.trace_processor)
        slice_query = slice_builder._create_slice_query_from_name(slice_spec)
        return slice_query.first()
