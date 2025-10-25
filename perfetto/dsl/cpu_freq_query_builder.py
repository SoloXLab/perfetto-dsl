"""
CPU频率查询构建器

提供链式调用的CPU频率分析功能，支持按CPU核心和频点分析运行时长
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class CpuFreqData:
    """CPU频率数据"""
    cpu_id: int
    freq_mhz: float
    total_duration_ns: int
    duration_percentage: float

    @property
    def total_duration_ms(self) -> float:
        """总时长（毫秒）"""
        return self.total_duration_ns / 1_000_000

    def __str__(self) -> str:
        return (f"CpuFreq(cpu={self.cpu_id}, "
                f"freq={self.freq_mhz:.0f}MHz, "
                f"duration={self.total_duration_ms:.2f}ms, "
                f"percentage={self.duration_percentage:.2f}%)")

    def __repr__(self) -> str:
        return (f"CpuFreqData(cpu_id={self.cpu_id}, "
                f"freq_mhz={self.freq_mhz}, "
                f"total_duration_ns={self.total_duration_ns}, "
                f"duration_percentage={self.duration_percentage})")


class CpuFreqQueryBuilder:
    """CPU频率查询构建器"""

    def __init__(self, trace_processor, **kwargs):
        self.trace_processor = trace_processor

        # 执行状态
        self._executed = False
        self._results: List[CpuFreqData] = []

        # 默认返回模式
        self._return_cpu_dict = True
        self._return_workload_dict = False
        self._return_process_dict = False
        self._return_thread_dict = False

        # CPU分组信息
        self._cpu_groups = None

        # 过滤条件
        self.where_conditions = []
        self.time_conditions = []

        # 初始化参数
        for key, func in [
            ('cpu', self.cpu),
            ('process', self.process),
            ('thread', self.thread),
            ('after', self.after),
            ('before', self.before),
            ('between', self.between),
        ]:
            if key in kwargs:
                func(kwargs[key])

    # ======== 辅助函数 ========

    def _build_base_sql(self) -> str:
        """统一构建 SQL 前置模板"""
        conditions = self.where_conditions + self.time_conditions
        where_clause = f" AND {' AND '.join(conditions)}" if conditions else ""

        return f"""
            WITH freq_periods AS (
                SELECT
                    CAST(args.display_value AS int) AS cpu,
                    counter.ts AS start_ts,
                    counter.value AS freq_mhz,
                    LEAD(counter.ts) OVER (
                        PARTITION BY args.display_value
                        ORDER BY counter.ts
                    ) AS end_ts
                FROM counter
                JOIN track ON counter.track_id = track.id
                JOIN args ON track.dimension_arg_set_id = args.arg_set_id
                WHERE track.type = 'cpu_frequency'{where_clause}
            )
        """

    def _check_cpu_frequency_tracks(self):
        """
            检查是否存在 cpu_frequency 类型的 track，如果不存在则抛出异常
        """

        check_sql = "SELECT COUNT(*) as count FROM track WHERE type = 'cpu_frequency'"
        result = self.trace_processor.query(check_sql)
        count = 0
        for row in result:
            count = row.count
            break
        
        if count == 0:
            error_msg = f"没有找到任何频率相关的 track 类型。\n"
            error_msg += f"请确保 trace 收集时启用了 CPU 频率监控。"
            
            raise ValueError(error_msg)
            
     

    def _query(self, sql: str):
        """安全执行 SQL"""
        try:
            return self.trace_processor.query(sql)
        except Exception as e:
            # 如果是检查 track 的查询，直接抛出异常
            if "COUNT(*) as count FROM track WHERE type = 'cpu_frequency'" in sql:
                raise
            print(f"[SQL 查询错误]: {e}\nSQL 片段:\n{sql[:300]}...")
            return []

    # ======== 条件构建 ========

    def cpu(self, cpu_id: Union[int, List[int], None] = None) -> 'CpuFreqQueryBuilder':
        """按CPU核心过滤"""
        self._return_cpu_dict = True
        self._return_workload_dict = False
        self._return_process_dict = False
        self._return_thread_dict = False

        if cpu_id is not None:
            if isinstance(cpu_id, int):
                self.where_conditions.append(f"CAST(args.display_value AS int) = {cpu_id}")
            else:
                cpu_list = ','.join(map(str, cpu_id))
                self.where_conditions.append(f"CAST(args.display_value AS int) IN ({cpu_list})")
        return self

    def process(self, name: Union[str, List[str], None] = None) -> 'CpuFreqQueryBuilder':
        """按进程过滤"""
        if name is None:
            # 没有参数时，返回所有进程的嵌套字典格式
            self._return_process_dict = True
        else:
            # 有参数时，过滤特定进程，返回CPU频点字典
            names = [name] if isinstance(name, str) else name
            cond = " OR ".join(f"process.name LIKE '{n}'" for n in names)
            self.where_conditions.append(f"({cond})")
        return self

    def thread(self, name: Union[str, List[str], None] = None) -> 'CpuFreqQueryBuilder':
        """按线程过滤"""
        if name is None:
            # 没有参数时，返回所有线程的嵌套字典格式
            self._return_thread_dict = True
        else:
            # 有参数时，过滤特定线程，返回CPU频点字典
            names = [name] if isinstance(name, str) else name
            cond = " OR ".join(f"thread.name LIKE '{n}'" for n in names)
            self.where_conditions.append(f"({cond})")
        return self

    def group(self, **groups) -> 'CpuFreqQueryBuilder':
        """
        按CPU核心分组聚合

        示例:
            trace.cpu_freq().group(little=[0,1,2,3], big=[4,5,6,7])
        """
        self._cpu_groups = groups
        return self

    def after(self, slice_obj) -> 'CpuFreqQueryBuilder':
        """时间过滤：开始时间之后"""
        if isinstance(slice_obj, str):
            slice_obj = self._create_slice_from_spec(slice_obj)
        elif isinstance(slice_obj, int):
            # 兼容原来的时间戳参数
            self.time_conditions.append(f"counter.ts >= {slice_obj}")
            return self
        
        self.time_conditions.append(f"counter.ts >= {slice_obj.ts}")
        return self

    def before(self, slice_obj) -> 'CpuFreqQueryBuilder':
        """时间过滤：结束时间之前"""
        if isinstance(slice_obj, str):
            slice_obj = self._create_slice_from_spec(slice_obj)
        elif isinstance(slice_obj, int):
            # 兼容原来的时间戳参数
            self.time_conditions.append(f"counter.ts <= {slice_obj}")
            return self
        
        self.time_conditions.append(f"counter.ts <= {slice_obj.ts + slice_obj.dur}")
        return self

    def between(self, start_slice, end_slice=None) -> 'CpuFreqQueryBuilder':
        """时间过滤：两个slice之间"""
        if isinstance(start_slice, str):
            start_slice = self._create_slice_from_spec(start_slice)
        if end_slice and isinstance(end_slice, str):
            end_slice = self._create_slice_from_spec(end_slice)
        
        if hasattr(start_slice, 'ts'):
            start_time = start_slice.ts
            end_time = start_slice.ts + start_slice.dur if end_slice is None else end_slice.ts + end_slice.dur
        else:
            start_time, end_time = start_slice, end_slice

        self.time_conditions += [
            f"counter.ts >= {start_time}",
            f"counter.ts <= {end_time}"
        ]
        return self

    # ======== 聚合查询与结果构建 ========

    # ...（中间 SQL 查询逻辑略）

    # ======== 主查询 ========

    def _build_query(self) -> str:
        print("构建主查询SQL")
        """构建主查询SQL"""
        return f"""
            {self._build_base_sql()}
            SELECT
                cpu,
                freq_mhz,
                SUM(
                    COALESCE(end_ts, (SELECT MAX(ts) FROM counter) + 1000000) - start_ts
                ) AS total_duration_ns
            FROM freq_periods
            WHERE end_ts IS NOT NULL OR start_ts IS NOT NULL
            GROUP BY cpu, freq_mhz
            ORDER BY cpu, freq_mhz
        """

    def _execute_query(self) -> List[CpuFreqData]:
        """执行查询并返回结果"""
        if self._executed:
            return self._results

        # 首先检查是否存在 cpu_frequency 类型的 track
        print("检查是否存在 cpu_frequency 类型的 track")
        self._check_cpu_frequency_tracks()
        
        sql = self._build_query()
        result = self._query(sql)
        self._results = [
            CpuFreqData(
                cpu_id=r.cpu,
                freq_mhz=r.freq_mhz,
                total_duration_ns=r.total_duration_ns,
                duration_percentage=0.0
            )
            for r in result
        ]
        self._executed = True
        return self._results

    # ======== 统计输出 ========

    def _get_grouped_usage(self, group_by: List[str]) -> Dict:
        """获取分组使用情况"""
        group_clause = ", ".join(group_by)
        sql = f"""
        {self._build_base_sql()}
        SELECT {group_clause},
               AVG(fp.freq_mhz) AS avg_freq_mhz,
               MAX(fp.freq_mhz) AS max_freq_mhz,
               MIN(fp.freq_mhz) AS min_freq_mhz,
               COUNT(*) AS freq_count
        FROM freq_periods fp
        GROUP BY {group_clause}
        ORDER BY avg_freq_mhz DESC
        """
        result = self._query(sql)
        data = {}

        for row in result:
            fields = {k: getattr(row, k, '') for k in group_by}
            avg_freq = getattr(row, 'avg_freq_mhz', 0)
            max_freq = getattr(row, 'max_freq_mhz', 0)
            min_freq = getattr(row, 'min_freq_mhz', 0)
            count = getattr(row, 'freq_count', 0)

            freq_data = {
                'avg_freq_mhz': round(avg_freq, 2),
                'max_freq_mhz': round(max_freq, 2),
                'min_freq_mhz': round(min_freq, 2),
                'count': count
            }

            d = data
            for k in group_by[:-1]:
                d = d.setdefault(fields[k], {})
            d[fields[group_by[-1]]] = freq_data

        return data

    def _get_nested_usage(self, group_by: List[str]) -> Dict:
        """获取嵌套使用情况"""
        group_clause = ", ".join(group_by)
        sql = f"""
        {self._build_base_sql()}
        SELECT {group_clause},
               AVG(fp.freq_mhz) AS avg_freq_mhz,
               MAX(fp.freq_mhz) AS max_freq_mhz,
               MIN(fp.freq_mhz) AS min_freq_mhz,
               COUNT(*) AS freq_count
        FROM freq_periods fp
        GROUP BY {group_clause}
        ORDER BY avg_freq_mhz DESC
        """
        result = self._query(sql)
        data = {}

        for row in result:
            fields = {k: getattr(row, k, '') for k in group_by}
            avg_freq = getattr(row, 'avg_freq_mhz', 0)
            max_freq = getattr(row, 'max_freq_mhz', 0)
            min_freq = getattr(row, 'min_freq_mhz', 0)
            count = getattr(row, 'freq_count', 0)

            freq_data = {
                'avg_freq_mhz': round(avg_freq, 2),
                'max_freq_mhz': round(max_freq, 2),
                'min_freq_mhz': round(min_freq, 2),
                'count': count
            }

            d = data
            for k in group_by[:-1]:
                d = d.setdefault(fields[k], {})
            d[fields[group_by[-1]]] = freq_data

        return data

    def total_duration(self) -> float:
        """获取总运行时长（毫秒）"""
        results = self._execute_query()
        if not results:
            return 0.0
        return sum(r.total_duration_ns for r in results) / 1_000_000.0

    # ======== 接口实现 ========

    def __str__(self) -> str:
        """字符串表示 - 懒加载，根据查询类型返回不同格式"""
        import json
        
        # 检查是否有过滤条件（where_conditions）
        has_filters = len(self.where_conditions) > 0
        
        # 1. 如果有过滤条件，返回过滤后的CPU频点字典
        if has_filters:
            cpu_freq_dict = self._get_cpu_freq_dict()
            # 如果有分组，应用分组逻辑
            if self._cpu_groups:
                cpu_freq_dict = self._apply_grouping(cpu_freq_dict)
            return json.dumps(cpu_freq_dict, indent=2, ensure_ascii=False)
        
        # 2. 如果没有任何特殊标志，返回CPU频点字典
        if not any([self._return_process_dict, self._return_thread_dict]):
            cpu_freq_dict = self._get_cpu_freq_dict()
            # 如果有分组，应用分组逻辑
            if self._cpu_groups:
                cpu_freq_dict = self._apply_grouping(cpu_freq_dict)
            return json.dumps(cpu_freq_dict, indent=2, ensure_ascii=False)
        
        # 3. 如果设置了 process 标志，返回进程嵌套字典
        if self._return_process_dict and not self._return_thread_dict:
            process_dict = self._get_process_freq_dict()
            # 如果有分组，应用分组逻辑到每个进程
            if self._cpu_groups:
                for process_name in process_dict:
                    process_dict[process_name] = self._apply_grouping(process_dict[process_name])
            return json.dumps(process_dict, indent=2, ensure_ascii=False)
        
        # 4. 如果设置了 thread 标志，返回线程嵌套字典
        if self._return_thread_dict and not self._return_process_dict:
            thread_dict = self._get_thread_freq_dict()
            # 如果有分组，应用分组逻辑到每个线程
            if self._cpu_groups:
                for thread_name in thread_dict:
                    thread_dict[thread_name] = self._apply_grouping(thread_dict[thread_name])
            return json.dumps(thread_dict, indent=2, ensure_ascii=False)
        
        # 5. 如果同时设置了 process 和 thread，返回进程-线程嵌套字典
        if self._return_process_dict and self._return_thread_dict:
            nested_dict = self._get_nested_freq_dict()
            # 如果有分组，应用分组逻辑到每个进程的每个线程
            if self._cpu_groups:
                for process_name in nested_dict:
                    for thread_name in nested_dict[process_name]:
                        nested_dict[process_name][thread_name] = self._apply_grouping(nested_dict[process_name][thread_name])
            return json.dumps(nested_dict, indent=2, ensure_ascii=False)
        
        # 6. 否则返回数据列表
        results = self._execute_query()
        if len(results) == 0:
            return "CpuFreqQueryBuilder: No results"
        else:
            # 直接输出所有结果的字符串表示
            result_strings = [str(result) for result in results]
            return '\n'.join(result_strings)

    def __repr__(self) -> str:
        return f"{self.total_duration():.4f}ms"
    
    def __iter__(self):
        """支持迭代"""
        return iter(self._execute_query())
    
    def __len__(self):
        """返回结果数量"""
        return len(self._execute_query())
    
    def get_stats(self) -> Dict:
        """获取统计信息（JSON格式）"""
        import json
        if self._return_process_dict and self._return_thread_dict:
            return self._get_nested_usage(
                ["process_name", "thread_name", "cpu", "freq_mhz"])
        if self._return_thread_dict:
            return self._get_nested_usage(
                ["thread_name", "cpu", "freq_mhz"])
        if self._return_process_dict:
            return self._get_nested_usage(
                ["process_name", "cpu", "freq_mhz"])
        if self._return_cpu_dict:
            return self._get_grouped_usage(
                ["cpu", "freq_mhz"])
        return {}
    
    def get_stats_json(self) -> str:
        """获取统计信息（JSON字符串格式）"""
        import json
        return json.dumps(self.get_stats(), indent=2, ensure_ascii=False)
    
    def _create_slice_from_spec(self, slice_spec: str):
        """从slice规格字符串创建Slice对象"""
        from .slice_query_builder import SliceQueryBuilder
        
        # 创建SliceQueryBuilder来查找slice
        slice_builder = SliceQueryBuilder(self.trace_processor)
        slice_query = slice_builder._create_slice_query_from_name(slice_spec)
        return slice_query.first()

    # ======== 新增的字典生成方法 ========
    
    def _get_cpu_freq_dict(self) -> Dict[str, Dict[str, int]]:
        """获取CPU频点字典格式的数据
        
        Returns:
            Dict[str, Dict[str, int]]: {'cpu_id': {'freq_mhz': duration_ns}}
        """
        # 如果有过滤条件，需要重新构建查询
        if len(self.where_conditions) > 0:
            sql = self._build_filtered_cpu_freq_query()
            result = self._query(sql)
            cpu_freq_dict = {}
            
            for row in result:
                cpu_id = str(getattr(row, 'cpu', 0))
                freq_mhz = str(int(getattr(row, 'freq_mhz', 0)))
                duration_ns = getattr(row, 'total_duration_ns', 0)
                
                if cpu_id not in cpu_freq_dict:
                    cpu_freq_dict[cpu_id] = {}
                
                if freq_mhz in cpu_freq_dict[cpu_id]:
                    cpu_freq_dict[cpu_id][freq_mhz] += duration_ns
                else:
                    cpu_freq_dict[cpu_id][freq_mhz] = duration_ns
            
            return cpu_freq_dict
        else:
            # 没有过滤条件，使用原有逻辑
            results = self._execute_query()
            cpu_freq_dict = {}
            
            for result in results:
                cpu_id = str(result.cpu_id)
                freq_mhz = str(int(result.freq_mhz))
                duration_ns = result.total_duration_ns
                
                if cpu_id not in cpu_freq_dict:
                    cpu_freq_dict[cpu_id] = {}
                
                if freq_mhz in cpu_freq_dict[cpu_id]:
                    cpu_freq_dict[cpu_id][freq_mhz] += duration_ns
                else:
                    cpu_freq_dict[cpu_id][freq_mhz] = duration_ns
            
            return cpu_freq_dict
    
    def _get_process_freq_dict(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """获取进程嵌套字典格式的数据
        
        Returns:
            Dict[str, Dict[str, Dict[str, int]]]: {'process_name': {'cpu_id': {'freq_mhz': duration_ns}}}
        """
        # 需要重新构建查询以包含进程信息
        sql = self._build_process_freq_query()
        result = self._query(sql)
        
        process_dict = {}
        for row in result:
            process_name = getattr(row, 'process_name', 'unknown')
            cpu_id = str(getattr(row, 'cpu', 0))
            freq_mhz = str(int(getattr(row, 'freq_mhz', 0)))
            duration_ns = getattr(row, 'total_duration_ns', 0)
            
            if process_name not in process_dict:
                process_dict[process_name] = {}
            if cpu_id not in process_dict[process_name]:
                process_dict[process_name][cpu_id] = {}
            
            if freq_mhz in process_dict[process_name][cpu_id]:
                process_dict[process_name][cpu_id][freq_mhz] += duration_ns
            else:
                process_dict[process_name][cpu_id][freq_mhz] = duration_ns
        
        return process_dict
    
    def _get_thread_freq_dict(self) -> Dict[str, Dict[str, Dict[str, int]]]:
        """获取线程嵌套字典格式的数据
        
        Returns:
            Dict[str, Dict[str, Dict[str, int]]]: {'thread_name': {'cpu_id': {'freq_mhz': duration_ns}}}
        """
        # 需要重新构建查询以包含线程信息
        sql = self._build_thread_freq_query()
        result = self._query(sql)
        
        thread_dict = {}
        for row in result:
            thread_name = getattr(row, 'thread_name', 'unknown')
            cpu_id = str(getattr(row, 'cpu', 0))
            freq_mhz = str(int(getattr(row, 'freq_mhz', 0)))
            duration_ns = getattr(row, 'total_duration_ns', 0)
            
            if thread_name not in thread_dict:
                thread_dict[thread_name] = {}
            if cpu_id not in thread_dict[thread_name]:
                thread_dict[thread_name][cpu_id] = {}
            
            if freq_mhz in thread_dict[thread_name][cpu_id]:
                thread_dict[thread_name][cpu_id][freq_mhz] += duration_ns
            else:
                thread_dict[thread_name][cpu_id][freq_mhz] = duration_ns
        
        return thread_dict
    
    def _get_nested_freq_dict(self) -> Dict[str, Dict[str, Dict[str, Dict[str, int]]]]:
        """获取进程-线程嵌套字典格式的数据
        
        Returns:
            Dict[str, Dict[str, Dict[str, Dict[str, int]]]]: {'process_name': {'thread_name': {'cpu_id': {'freq_mhz': duration_ns}}}}
        """
        # 需要重新构建查询以包含进程和线程信息
        sql = self._build_nested_freq_query()
        result = self._query(sql)
        
        nested_dict = {}
        for row in result:
            process_name = getattr(row, 'process_name', 'unknown')
            thread_name = getattr(row, 'thread_name', 'unknown')
            cpu_id = str(getattr(row, 'cpu', 0))
            freq_mhz = str(int(getattr(row, 'freq_mhz', 0)))
            duration_ns = getattr(row, 'total_duration_ns', 0)
            
            if process_name not in nested_dict:
                nested_dict[process_name] = {}
            if thread_name not in nested_dict[process_name]:
                nested_dict[process_name][thread_name] = {}
            if cpu_id not in nested_dict[process_name][thread_name]:
                nested_dict[process_name][thread_name][cpu_id] = {}
            
            if freq_mhz in nested_dict[process_name][thread_name][cpu_id]:
                nested_dict[process_name][thread_name][cpu_id][freq_mhz] += duration_ns
            else:
                nested_dict[process_name][thread_name][cpu_id][freq_mhz] = duration_ns
        
        return nested_dict
    
    def _build_process_freq_query(self) -> str:
        """构建包含进程信息的频率查询"""
        # 分离时间条件和进程过滤条件
        time_conditions = self.time_conditions
        process_conditions = [cond for cond in self.where_conditions if 'process.name' in cond]
        
        time_clause = f" AND {' AND '.join(time_conditions)}" if time_conditions else ""
        process_clause = f" AND {' AND '.join(process_conditions)}" if process_conditions else ""
        
        return f"""
            WITH freq_periods AS (
                SELECT
                    CAST(args.display_value AS int) AS cpu,
                    counter.ts AS start_ts,
                    counter.value AS freq_mhz,
                    LEAD(counter.ts) OVER (
                        PARTITION BY args.display_value
                        ORDER BY counter.ts
                    ) AS end_ts
                FROM counter
                JOIN track ON counter.track_id = track.id
                JOIN args ON track.dimension_arg_set_id = args.arg_set_id
                WHERE track.type = 'cpu_frequency'{time_clause}
            ),
            sched_with_freq AS (
                SELECT 
                    s.ucpu,
                    s.ts,
                    s.dur,
                    fp.freq_mhz,
                    process.name AS process_name
                FROM sched s
                JOIN thread ON s.utid = thread.utid
                JOIN process ON thread.upid = process.upid
                JOIN freq_periods fp ON s.ucpu = fp.cpu 
                    AND s.ts >= fp.start_ts 
                    AND s.ts < COALESCE(fp.end_ts, s.ts + s.dur)
                WHERE 1=1{process_clause}
            )
            SELECT
                process_name,
                ucpu AS cpu,
                freq_mhz,
                SUM(dur) AS total_duration_ns
            FROM sched_with_freq
            GROUP BY process_name, ucpu, freq_mhz
            ORDER BY process_name, ucpu, freq_mhz
        """
    
    def _build_thread_freq_query(self) -> str:
        """构建包含线程信息的频率查询"""
        # 分离时间条件和线程过滤条件
        time_conditions = self.time_conditions
        thread_conditions = [cond for cond in self.where_conditions if 'thread.name' in cond]
        
        time_clause = f" AND {' AND '.join(time_conditions)}" if time_conditions else ""
        thread_clause = f" AND {' AND '.join(thread_conditions)}" if thread_conditions else ""
        
        return f"""
            WITH freq_periods AS (
                SELECT
                    CAST(args.display_value AS int) AS cpu,
                    counter.ts AS start_ts,
                    counter.value AS freq_mhz,
                    LEAD(counter.ts) OVER (
                        PARTITION BY args.display_value
                        ORDER BY counter.ts
                    ) AS end_ts
                FROM counter
                JOIN track ON counter.track_id = track.id
                JOIN args ON track.dimension_arg_set_id = args.arg_set_id
                WHERE track.type = 'cpu_frequency'{time_clause}
            ),
            sched_with_freq AS (
                SELECT 
                    s.ucpu,
                    s.ts,
                    s.dur,
                    fp.freq_mhz,
                    thread.name AS thread_name
                FROM sched s
                JOIN thread ON s.utid = thread.utid
                JOIN freq_periods fp ON s.ucpu = fp.cpu 
                    AND s.ts >= fp.start_ts 
                    AND s.ts < COALESCE(fp.end_ts, s.ts + s.dur)
                WHERE 1=1{thread_clause}
            )
            SELECT
                thread_name,
                ucpu AS cpu,
                freq_mhz,
                SUM(dur) AS total_duration_ns
            FROM sched_with_freq
            GROUP BY thread_name, ucpu, freq_mhz
            ORDER BY thread_name, ucpu, freq_mhz
        """
    
    def _build_nested_freq_query(self) -> str:
        """构建包含进程和线程信息的频率查询"""
        # 分离时间条件和过滤条件
        time_conditions = self.time_conditions
        filter_conditions = [cond for cond in self.where_conditions if 'process.name' in cond or 'thread.name' in cond]
        
        time_clause = f" AND {' AND '.join(time_conditions)}" if time_conditions else ""
        filter_clause = f" AND {' AND '.join(filter_conditions)}" if filter_conditions else ""
        
        return f"""
            WITH freq_periods AS (
                SELECT
                    CAST(args.display_value AS int) AS cpu,
                    counter.ts AS start_ts,
                    counter.value AS freq_mhz,
                    LEAD(counter.ts) OVER (
                        PARTITION BY args.display_value
                        ORDER BY counter.ts
                    ) AS end_ts
                FROM counter
                JOIN track ON counter.track_id = track.id
                JOIN args ON track.dimension_arg_set_id = args.arg_set_id
                WHERE track.type = 'cpu_frequency'{time_clause}
            ),
            sched_with_freq AS (
                SELECT 
                    s.ucpu,
                    s.ts,
                    s.dur,
                    fp.freq_mhz,
                    process.name AS process_name,
                    thread.name AS thread_name
                FROM sched s
                JOIN thread ON s.utid = thread.utid
                JOIN process ON thread.upid = process.upid
                JOIN freq_periods fp ON s.ucpu = fp.cpu 
                    AND s.ts >= fp.start_ts 
                    AND s.ts < COALESCE(fp.end_ts, s.ts + s.dur)
                WHERE 1=1{filter_clause}
            )
            SELECT
                process_name,
                thread_name,
                ucpu AS cpu,
                freq_mhz,
                SUM(dur) AS total_duration_ns
            FROM sched_with_freq
            GROUP BY process_name, thread_name, ucpu, freq_mhz
            ORDER BY process_name, thread_name, ucpu, freq_mhz
        """
    
    def _build_filtered_cpu_freq_query(self) -> str:
        """构建过滤后的CPU频点查询"""
        # 分离时间条件和过滤条件
        time_conditions = self.time_conditions
        filter_conditions = [cond for cond in self.where_conditions if 'process.name' in cond or 'thread.name' in cond]
        
        time_clause = f" AND {' AND '.join(time_conditions)}" if time_conditions else ""
        filter_clause = f" AND {' AND '.join(filter_conditions)}" if filter_conditions else ""
        
        return f"""
            WITH freq_periods AS (
                SELECT
                    CAST(args.display_value AS int) AS cpu,
                    counter.ts AS start_ts,
                    counter.value AS freq_mhz,
                    LEAD(counter.ts) OVER (
                        PARTITION BY args.display_value
                        ORDER BY counter.ts
                    ) AS end_ts
                FROM counter
                JOIN track ON counter.track_id = track.id
                JOIN args ON track.dimension_arg_set_id = args.arg_set_id
                WHERE track.type = 'cpu_frequency'{time_clause}
            ),
            sched_with_freq AS (
                SELECT 
                    s.ucpu,
                    s.ts,
                    s.dur,
                    fp.freq_mhz
                FROM sched s
                JOIN thread ON s.utid = thread.utid
                JOIN process ON thread.upid = process.upid
                JOIN freq_periods fp ON s.ucpu = fp.cpu 
                    AND s.ts >= fp.start_ts 
                    AND s.ts < COALESCE(fp.end_ts, s.ts + s.dur)
                WHERE 1=1{filter_clause}
            )
            SELECT
                ucpu AS cpu,
                freq_mhz,
                SUM(dur) AS total_duration_ns
            FROM sched_with_freq
            GROUP BY ucpu, freq_mhz
            ORDER BY ucpu, freq_mhz
        """
    
    def _apply_grouping(self, cpu_freq_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, int]]:
        """应用CPU分组逻辑
        
        Args:
            cpu_freq_dict: 原始CPU频点字典 {'cpu_id': {'freq_mhz': duration_ns}}
            
        Returns:
            Dict[str, Dict[str, int]]: 分组后的字典 {'group_name': {'freq_mhz': total_duration_ns}}
        """
        if not self._cpu_groups:
            return cpu_freq_dict
        
        grouped_dict = {}
        
        for group_name, cpu_list in self._cpu_groups.items():
            # 初始化组字典
            grouped_dict[group_name] = {}
            
            # 遍历该组中的所有CPU
            for cpu_id in cpu_list:
                cpu_str = str(cpu_id)
                if cpu_str in cpu_freq_dict:
                    # 合并该CPU的所有频点数据
                    for freq_mhz, duration_ns in cpu_freq_dict[cpu_str].items():
                        if freq_mhz in grouped_dict[group_name]:
                            grouped_dict[group_name][freq_mhz] += duration_ns
                        else:
                            grouped_dict[group_name][freq_mhz] = duration_ns
        
        return grouped_dict
