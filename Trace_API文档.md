# Trace() 对象 API 文档

本文档详细列出了 `Trace()` 创建的对象支持的所有 API、返回对象类型以及对象的属性。

## 目录
1. [Trace 类方法](#trace-类方法)
2. [SliceQueryBuilder 及其返回对象](#slicequerybuilder-及其返回对象)
3. [CounterQueryBuilder 及其返回对象](#counterquerybuilder-及其返回对象)
4. [CpuFreqQueryBuilder 及其返回对象](#cpufreqquerybuilder-及其返回对象)
5. [CpuUsageQueryBuilder 及其返回对象](#cpuusagequerybuilder-及其返回对象)
6. [MetricQueryBuilder 及其返回对象](#metricquerybuilder-及其返回对象)

---

## Trace 类方法

### 1. `slice(**kwargs) -> SliceQueryBuilder`
开始 slice 查询

**参数：**
- `**kwargs`: 可选的过滤条件，如 `name`, `id`, `process`, `thread` 等

**返回：** `SliceQueryBuilder` 对象

**示例：**
```python
trace.slice(name="doFrame")
trace.slice(id=123)
trace.slice(name="doFrame|process:system_server")
```

---

### 2. `counter(**kwargs) -> CounterQueryBuilder`
开始 counter 查询

**参数：**
- `**kwargs`: 可选的过滤条件，如 `name`, `process_name`, `process_id`, `track_id` 等

**返回：** `CounterQueryBuilder` 对象

**示例：**
```python
trace.counter(name="cpu_freq")
trace.counter(process_name="system_server")
```

---

### 3. `cpu_freq(**kwargs) -> CpuFreqQueryBuilder`
开始 CPU 频率查询

**参数：**
- `**kwargs`: 可选的过滤条件，如 `cpu`, `process`, `thread`, `after`, `before`, `between` 等

**返回：** `CpuFreqQueryBuilder` 对象

**示例：**
```python
trace.cpu_freq()
trace.cpu_freq(cpu=0)
trace.cpu_freq().process()
trace.cpu_freq().group(little=[0,1,2,3], big=[4,5,6,7])
```

---

### 4. `cpu_usage(**kwargs) -> CpuUsageQueryBuilder`
开始 CPU 使用率查询

**参数：**
- `**kwargs`: 可选的过滤条件，如 `process_name`, `thread_name`, `cpu_id` 等

**返回：** `CpuUsageQueryBuilder` 对象

**示例：**
```python
trace.cpu_usage()
trace.cpu_usage().process()
trace.cpu_usage().thread()
trace.cpu_usage().process("system_server")
```

---

### 5. `metric(metric_name: str = None, **kwargs) -> List[str] | Dict[str, Any]`
开始 metric 查询

**参数：**
- `metric_name`: metric 名称，如果不提供则返回所有可用的 metrics 列表
- `**kwargs`: 传递给 metric 的额外参数

**返回：**
- 如果提供了 `metric_name`，返回 `Dict[str, Any]`（metric 结果字典）
- 如果没有提供 `metric_name`，返回 `List[str]`（所有可用的 metrics 字符串列表）

**示例：**
```python
all_metrics = trace.metric()  # 返回所有可用的 metrics 列表
result = trace.metric("android_cpu")  # 返回指定 metric 的结果字典
```

---

## SliceQueryBuilder 及其返回对象

### SliceQueryBuilder 方法

#### 查询构建方法
- `slice(**kwargs) -> SliceQueryBuilder`: 添加 slice 查询条件
- `track(**kwargs) -> SliceQueryBuilder`: 按 track 过滤或查询 track
- `process(**kwargs) -> SliceQueryBuilder`: 按进程过滤
- `thread(**kwargs) -> SliceQueryBuilder`: 按线程过滤
- `parent(level=1, **kwargs) -> SliceQueryBuilder`: 查询父节点
- `children(**kwargs) -> SliceQueryBuilder`: 查询子节点
- `flow_out(**kwargs) -> SliceQueryBuilder`: 查询 flow_out 关联的 slice
- `flow_in(**kwargs) -> SliceQueryBuilder`: 查询 flow_in 关联的 slice
- `counter(**kwargs) -> SliceQueryBuilder`: 查询关联的 counter
- `flow(**kwargs) -> SliceQueryBuilder`: 查询关联的 flow
- `args(**kwargs) -> SliceQueryBuilder`: 按 args 参数过滤
- `time_range(start_ts, end_ts) -> SliceQueryBuilder`: 按时间范围过滤
- `limit(count) -> SliceQueryBuilder`: 限制结果数量
- `order_by(clause) -> SliceQueryBuilder`: 添加排序条件

#### 结果获取方法
- `all() -> List[Slice]`: 获取所有结果
- `first() -> Slice | None`: 获取第一个结果
- `last() -> Slice | None`: 获取最后一个结果
- `count() -> int`: 获取结果数量

#### 其他方法
- `__iter__()`: 支持迭代
- `__getitem__(index)`: 支持索引访问
- `__len__()`: 支持 `len()` 函数
- `__bool__()`: 支持布尔判断

### Slice 对象属性

#### 基础属性
- `id: int` - Slice ID
- `name: str` - Slice 名称
- `ts: int` - 开始时间戳（纳秒）
- `dur: int` - 持续时间（纳秒）
- `pid: int` - 进程 ID
- `tid: int` - 线程 ID
- `cat: Optional[str]` - 类别
- `track_id: int` - Track ID
- `depth: Optional[int]` - 深度
- `parent_id: Optional[int]` - 父节点 ID
- `arg_set_id: Optional[int]` - 参数集 ID

#### 时间属性（Property）
- `start_time_ns: int` - 开始时间（纳秒）
- `end_time_ns: int` - 结束时间（纳秒）
- `duration_ns: int` - 持续时间（纳秒）
- `start_time_ms: float` - 开始时间（毫秒）
- `end_time_ms: float` - 结束时间（毫秒）
- `duration_ms: float` - 持续时间（毫秒）

#### 关联对象属性（Property）
- `related: RelatedObjectsAccessor` - 关联对象访问器
- `process` - 进程信息（字典，包含 `upid`, `name`, `pid`）
- `thread` - 线程信息（字典，包含 `utid`, `name`, `tid`, `is_main_thread`）
- `track: Track` - Track 对象

#### 方法
- `get_process_name() -> str` - 获取进程名
- `get_thread_name() -> str` - 获取线程名
- `get_track_name() -> str` - 获取 track 名
- `get_upid() -> Optional[int]` - 获取进程的 upid
- `get_utid() -> Optional[int]` - 获取线程的 utid
- `get_pid() -> Optional[int]` - 获取进程的 pid
- `get_tid() -> Optional[int]` - 获取线程的 tid
- `get_args() -> Optional[Dict[str, Any]]` - 获取 slice 的 args 参数
- `get_arg(key: str, default: Any = None) -> Any` - 获取指定参数值
- `input_id(default: str = None) -> Optional[str]` - 从 slice name 中提取 id=0x... 格式的 ID
- `frame_id(default: int = None) -> Optional[int]` - 从 slice name 中提取 Choreographer#doFrame 后的帧号
- `overlaps_with(other: Slice) -> bool` - 检查是否与另一个 slice 重叠
- `contains_timestamp(timestamp_ms: float) -> bool` - 检查是否包含指定时间戳（毫秒）
- `contains(timestamp_ns: int) -> bool` - 检查是否包含指定时间戳（纳秒）
- `parent(level: int = 1, **kwargs) -> SliceQueryBuilder` - 查找父节点，支持链式调用
- `flow_out(**kwargs) -> SliceQueryBuilder` - 查找 flow_out 关联的 slice
- `flow_in(**kwargs) -> SliceQueryBuilder` - 查找 flow_in 关联的 slice

---

## CounterQueryBuilder 及其返回对象

### CounterQueryBuilder 方法

#### 查询构建方法
- `name(name) -> CounterQueryBuilder`: 按 counter 名称过滤
- `process(name) -> CounterQueryBuilder`: 按进程名称过滤
- `track_id(track_id) -> CounterQueryBuilder`: 按 track ID 过滤
- `value_range(min_value, max_value) -> CounterQueryBuilder`: 按 counter 值范围过滤
- `time_range(start_ts, end_ts) -> CounterQueryBuilder`: 按时间范围过滤
- `limit(count) -> CounterQueryBuilder`: 限制结果数量
- `order_by(clause) -> CounterQueryBuilder`: 添加排序条件

#### 结果获取方法
- `all() -> List[Counter]`: 获取所有结果
- `first() -> Counter | None`: 获取第一个结果
- `last() -> Counter | None`: 获取最后一个结果
- `count() -> int`: 获取结果数量

#### 统计方法
- `max(field='value') -> Optional[float]`: 获取指定字段的最大值
- `min(field='value') -> Optional[float]`: 获取指定字段的最小值
- `avg(field='value') -> Optional[float]`: 获取指定字段的平均值

#### 其他方法
- `__iter__()`: 支持迭代
- `__getitem__(index)`: 支持索引访问
- `__len__()`: 支持 `len()` 函数
- `__bool__()`: 支持布尔判断

### Counter 对象属性

#### 基础属性
- `id: int` - Counter ID
- `name: str` - Counter 名称
- `ts: int` - 时间戳（纳秒）
- `value: float` - Counter 值
- `track_id: int` - Track ID

#### 时间属性（Property）
- `timestamp_ns: int` - 时间戳（纳秒）
- `timestamp_ms: float` - 时间戳（毫秒）

#### 方法
- `to_dict() -> Dict[str, Any]`: 转换为字典
- `from_dict(data) -> Counter`: 从字典或 Row 对象创建 Counter 实例

---

## CpuFreqQueryBuilder 及其返回对象

### CpuFreqQueryBuilder 方法

#### 查询构建方法
- `cpu(cpu_id) -> CpuFreqQueryBuilder`: 按 CPU 核心过滤
- `process(name) -> CpuFreqQueryBuilder`: 按进程过滤（无参数时返回进程嵌套字典）
- `thread(name) -> CpuFreqQueryBuilder`: 按线程过滤（无参数时返回线程嵌套字典）
- `group(**groups) -> CpuFreqQueryBuilder`: 按 CPU 核心分组聚合（如 `little=[0,1,2,3], big=[4,5,6,7]`）
- `after(slice_obj) -> CpuFreqQueryBuilder`: 时间过滤：开始时间之后
- `before(slice_obj) -> CpuFreqQueryBuilder`: 时间过滤：结束时间之前
- `between(start_slice, end_slice) -> CpuFreqQueryBuilder`: 时间过滤：两个 slice 之间

#### 结果获取方法
- `total_duration() -> float`: 获取总运行时长（毫秒）

#### 统计方法
- `get_stats() -> Dict`: 获取统计信息（JSON 格式）
- `get_stats_json() -> str`: 获取统计信息（JSON 字符串格式）

#### 其他方法
- `__str__()`: 字符串表示（根据查询类型返回不同格式）
- `__repr__()`: 返回总运行时长
- `__iter__()`: 支持迭代
- `__len__()`: 返回结果数量

### 返回对象类型

根据调用方式，`CpuFreqQueryBuilder` 可能返回：

1. **CpuFreqData 对象列表**（通过 `_execute_query()` 或迭代）
2. **字典格式**（通过 `__str__()` 或直接使用）：
   - CPU 频点字典：`{'cpu_id': {'freq_mhz': duration_ns}}`
   - 进程嵌套字典：`{'process_name': {'cpu_id': {'freq_mhz': duration_ns}}}`
   - 线程嵌套字典：`{'thread_name': {'cpu_id': {'freq_mhz': duration_ns}}}`
   - 进程-线程嵌套字典：`{'process_name': {'thread_name': {'cpu_id': {'freq_mhz': duration_ns}}}}`

### CpuFreqData 对象属性

#### 基础属性
- `cpu_id: int` - CPU 核心 ID
- `freq_mhz: float` - 频率（MHz）
- `total_duration_ns: int` - 总运行时长（纳秒）
- `duration_percentage: float` - 运行时长百分比

#### 时间属性（Property）
- `total_duration_ms: float` - 总运行时长（毫秒）

---

## CpuUsageQueryBuilder 及其返回对象

### CpuUsageQueryBuilder 方法

#### 查询构建方法
- `process(name) -> CpuUsageQueryBuilder`: 按进程过滤（无参数时返回进程字典）
- `thread(name) -> CpuUsageQueryBuilder`: 按线程过滤（无参数时返回线程字典）
- `cpu(cpu_id) -> CpuUsageQueryBuilder`: 按 CPU 核心过滤（无参数时返回 CPU 字典）
- `after(slice_obj) -> CpuUsageQueryBuilder`: 时间过滤：开始时间之后
- `before(slice_obj) -> CpuUsageQueryBuilder`: 时间过滤：结束时间之前
- `between(start_slice, end_slice) -> CpuUsageQueryBuilder`: 时间过滤：两个 slice 之间

#### 结果获取方法
- `total_usage() -> float`: 获取整体 CPU 使用率（小数格式，1.0 = 100%）

#### 统计方法
- `get_stats() -> Dict`: 获取统计信息（JSON 格式）
- `get_stats_json() -> str`: 获取统计信息（JSON 字符串格式）

#### 其他方法
- `__str__()`: 字符串表示（根据查询类型返回不同格式）
- `__repr__()`: 返回总使用率百分比
- `__iter__()`: 支持迭代
- `__len__()`: 返回结果数量
- `__getitem__(key)`: 支持字典式访问
- `items()`: 返回字典的 items

### 返回对象类型

根据调用方式，`CpuUsageQueryBuilder` 可能返回：

1. **CpuUsageData 对象列表**（通过 `_execute_query()` 或迭代）
2. **float**（整体 CPU 使用率，通过 `total_usage()` 或 `__str__()`）
3. **字典格式**（通过 `__str__()` 或直接使用）：
   - 进程字典：`{'process_name': usage_ratio}`（按使用率从高到低排序）
   - 线程字典：`{'thread_name': usage_ratio}`（按使用率从高到低排序）
   - 进程-线程嵌套字典：`{'process_name': {'thread_name': usage_ratio}}`（按名字增序排序）
   - CPU 字典：`{'cpu_id': usage_ratio}`

### CpuUsageData 对象属性

#### 基础属性
- `process_name: Optional[str]` - 进程名
- `thread_name: Optional[str]` - 线程名
- `thread_id: int` - 线程 ID
- `total_runtime_ns: int` - 总运行时间（纳秒）
- `total_duration_ns: int` - 总持续时间（纳秒）
- `usage_percentage: float` - CPU 使用率百分比
- `cpu_count: int` - CPU 核心数量

#### 时间属性（Property）
- `total_runtime_ms: float` - 总运行时间（毫秒）
- `total_duration_ms: float` - 总持续时间（毫秒）

---

## MetricQueryBuilder 及其返回对象

### MetricQueryBuilder 方法

#### 查询方法
- `list_all() -> List[str]`: 列出所有可用的 metrics
- `execute(metric_name: str) -> Dict[str, Any]`: 执行指定的 metric
- `__call__(metric_name: str = None) -> List[str] | Dict[str, Any]`: 支持直接调用实例

### 返回对象类型

1. **List[str]**：当调用 `list_all()` 或 `metric()` 无参数时，返回所有可用的 metrics 名称列表
2. **Dict[str, Any]**：当调用 `execute(metric_name)` 或 `metric(metric_name)` 时，返回 metric 结果字典，格式为 `{metric_name: metric_data}`

---

## 使用示例

### 完整示例

```python
from perfetto.dsl import Trace

with Trace("trace_file.pftrace") as trace:
    # 1. Slice 查询
    slices = trace.slice(name="doFrame").limit(5).all()
    for slice_obj in slices:
        print(f"ID: {slice_obj.id}")
        print(f"Name: {slice_obj.name}")
        print(f"Time: {slice_obj.start_time_ms:.2f}ms - {slice_obj.end_time_ms:.2f}ms")
        print(f"Process: {slice_obj.get_process_name()}")
        print(f"Thread: {slice_obj.get_thread_name()}")
        
        # 查询 flow_out
        flow_out_slices = slice_obj.flow_out().all()
        print(f"Flow Out: {len(flow_out_slices)} slices")
    
    # 2. Counter 查询
    counters = trace.counter(name="cpu_freq").all()
    for counter in counters:
        print(f"Counter: {counter.name}, Value: {counter.value}, Time: {counter.timestamp_ms}ms")
    
    # 3. CPU 频率查询
    cpu_freq_dict = trace.cpu_freq()  # 返回字典格式
    print(cpu_freq_dict)
    
    # 4. CPU 使用率查询
    overall_usage = trace.cpu_usage()  # 返回整体使用率（小数格式）
    process_usage = trace.cpu_usage().process()  # 返回进程字典
    thread_usage = trace.cpu_usage().thread()  # 返回线程字典
    nested_usage = trace.cpu_usage().process().thread()  # 返回嵌套字典
    
    # 5. Metric 查询
    all_metrics = trace.metric()  # 返回所有可用的 metrics 列表
    metric_result = trace.metric("android_cpu")  # 返回指定 metric 的结果
```

---

## 注意事项

1. **Trace 对象应使用 `with` 语句**：确保正确关闭 TraceProcessor
2. **Slice 对象的关联对象访问**：需要先通过 `slice()` 查询获取的 Slice 对象才能访问 `related`、`process`、`thread`、`track` 等属性
3. **懒加载机制**：QueryBuilder 使用懒加载，只有在调用 `all()`、`first()`、`last()` 等方法时才会执行查询
4. **返回类型根据调用方式变化**：`CpuFreqQueryBuilder` 和 `CpuUsageQueryBuilder` 的返回类型会根据调用方式（是否有过滤条件、是否调用特定方法）而变化
