# Perfetto DSL

一个为 Perfetto trace 文件提供链式 DSL 访问的 Python 库，支持懒加载、关联对象属性访问、强大的 args 参数过滤和高级 slice 定位语法。

## ✨ 主要特性

- **🔗 链式 DSL**: 支持 `trace.slice(id=123).process(name="app").thread(name="main")` 的链式调用
- **⚡ 懒加载**: 查询只在需要时执行，提高性能
- **🔍 关联对象访问**: 支持 `slice.get_process_name()` 和 `slice.get_thread_name()` 的直接方法访问
- **📊 智能信息显示**: Slice 对象自动显示 process、thread、track 名称和 upid、utid、pid、tid 等完整信息
- **🎯 高级 Args 参数过滤**: 支持通过 slice 的 args 参数进行精确和模糊匹配过滤
- **🎯 高级 Slice 定位语法**: 支持 `slice_name|process_name||thread_name|||track_name#index` 的精确 slice 定位
- **🔄 Flow 关联查询**: 支持通过 flow 关系查找关联的 slice
- **📈 聚合统计**: 支持 count、max、min、avg、p90、p95 等聚合方法

## 🚀 快速开始

```bash
uv add perfetto-trace-dsl
# 或 pip install perfetto-trace-dsl
```

```python
from perfetto_trace_dsl import Trace

with Trace("trace_file.pftrace") as trace:
    slice_obj = trace.slice(id=123).first()
    slices = trace.slice(name="function_name").process(name="app_name").all()
```

---

## 📋 Trace().slice() API 参考

`trace.slice()` 返回 `SliceQueryBuilder`，用于构建 slice 查询并获取 `Slice` 对象。

### SliceQueryBuilder 查询构建方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `slice` | `slice(**kwargs) -> SliceQueryBuilder` | 开始 slice 查询，支持 `id`, `name`, `cat`, `duration_ms`, `ts`, `dur`, `depth`, `args`, `before`, `after`, `between`, `flow_out_name`, `flow_out_arg` 等参数 |
| `id` | `id(value: int) -> SliceQueryBuilder` | 按 slice ID 精确匹配 |
| `name` | `name(value: str) -> SliceQueryBuilder` | 按名称过滤，支持 `%` 通配符的 LIKE 匹配 |
| `ts` | `ts(op, value) -> SliceQueryBuilder` | 按开始时间戳过滤，op 支持 `=`, `>`, `>=`, `<`, `<=`, `!=`，value 为 int/float |
| `dur` | `dur(op, value) -> SliceQueryBuilder` | 按持续时间（纳秒）过滤 |
| `depth` | `depth(op, value) -> SliceQueryBuilder` | 按深度过滤 |
| `arg` | `arg(key: str) -> _SliceArgComparator` | 返回比较器，可链式 `.compare(op, value)` 进行 args 过滤 |
| `process` | `process(**kwargs) -> SliceQueryBuilder` | 按进程过滤，支持 `name`, `pid`, `upid` 等 |
| `thread` | `thread(**kwargs) -> SliceQueryBuilder` | 按线程过滤，支持 `name`, `tid`, `utid`, `main=True` 等 |
| `track` | `track(**kwargs) -> SliceQueryBuilder` | 按 track 过滤，支持 `name`, `type` 等 |
| `parent` | `parent(level=1, **kwargs) -> SliceQueryBuilder` | 查询父级 slice |
| `child` | `child(level=1, **kwargs) -> SliceQueryBuilder` | 查询子级 slice |
| `descendants` | `descendants(**kwargs) -> SliceQueryBuilder` | 递归查询所有子孙 slice |
| `siblings` | `siblings(**kwargs) -> SliceQueryBuilder` | 查询同级 slice |
| `args` | `args(**kwargs) -> SliceQueryBuilder` | 按 args 参数过滤，如 `args("Layer name", "Surface")` |
| `filter` | `filter(condition: str) -> SliceQueryBuilder` | 添加过滤条件，支持 `duration>=1.0`, `name='xxx'`, `id=123` 等 |
| `where` | `where(condition: str) -> SliceQueryBuilder` | 添加原始 SQL WHERE 条件 |
| `before` | `before(slice_obj) -> SliceQueryBuilder` | 查找在指定 slice 开始时间之前的 slice |
| `after` | `after(slice_obj) -> SliceQueryBuilder` | 查找在指定 slice 结束时间之后的 slice |
| `between` | `between(start_slice, end_slice=None) -> SliceQueryBuilder` | 查找在时间范围内的 slice，单参数时用该 slice 的时间范围 |
| `flow_out` | `flow_out(**kwargs) -> SliceQueryBuilder` | 查找通过 flow 关联的 slice_out |
| `flow_in` | `flow_in(**kwargs) -> SliceQueryBuilder` | 查找通过 flow 关联的 slice_in |
| `limit` | `limit(count: int) -> SliceQueryBuilder` | 限制结果数量 |
| `order_by` | `order_by(clause: str) -> SliceQueryBuilder` | 添加 ORDER BY 子句 |

### SliceQueryBuilder 结果获取方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `all` | `all() -> List[Slice]` | 获取所有结果 |
| `first` | `first() -> Optional[Slice]` | 获取第一个结果 |
| `last` | `last() -> Optional[Slice]` | 获取最后一个结果 |
| `count` | `count() -> int` | 获取结果数量（使用 SQL COUNT，高效） |
| `execute` | `execute() -> Slice \| List[Slice]` | 执行查询并返回结果 |

### SliceQueryBuilder 聚合统计方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `max` | `max(field='duration') -> float` | 获取指定字段最大值 |
| `min` | `min(field='duration') -> float` | 获取指定字段最小值 |
| `avg` | `avg(field='duration') -> float` | 获取指定字段平均值 |
| `p90` | `p90(field='duration') -> float` | 获取 90 分位数 |
| `p95` | `p95(field='duration') -> float` | 获取 95 分位数 |
| `median` | `median(field='duration') -> float` | 获取中位数 |

### SliceQueryBuilder 其他能力

| 能力 | 说明 |
|------|------|
| `__iter__` | 支持 `for s in trace.slice():` 迭代 |
| `__getitem__` | 支持 `trace.slice()[0]` 索引访问 |
| `__len__` | 支持 `len(trace.slice())` |
| `__bool__` | 支持 `if trace.slice():` 布尔判断 |
| `counter` | 切换到 counter 查询 |
| `flow` | 切换到 flow 查询 |
| `args(key)` | 返回所有 slice 对应 key 的值列表（`ArgsValues`） |
| `args()` | 返回所有 slice 的 args 字典列表 |

### ArgsValues 统计方法（由 `args(key)` 返回）

| 方法 | 说明 |
|------|------|
| `count()` | 值的总数（含 None） |
| `count_non_null()` | 非 None 值数量 |
| `max()` / `min()` | 最大/最小值 |
| `avg()` / `sum()` | 平均值/总和 |
| `unique()` | 唯一值列表 |
| `unique_count()` | 唯一值数量 |
| `__getitem__(index)` | 索引访问 |
| `__iter__` | 迭代 |

---

### Slice 对象属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | `int` | Slice ID |
| `name` | `str` | Slice 名称 |
| `ts` | `int` | 开始时间戳（纳秒） |
| `dur` | `int` | 持续时间（纳秒） |
| `pid` | `int` | 进程 ID |
| `tid` | `int` | 线程 ID |
| `cat` | `Optional[str]` | 类别 |
| `track_id` | `int` | Track ID |
| `depth` | `Optional[int]` | 深度 |
| `parent_id` | `Optional[int]` | 父节点 ID |
| `arg_set_id` | `Optional[int]` | 参数集 ID |
| `start_time_ns` | `int` | 开始时间（纳秒，property） |
| `end_time_ns` | `int` | 结束时间（纳秒，property） |
| `duration_ns` | `int` | 持续时间（纳秒，property） |
| `start_time_ms` | `float` | 开始时间（毫秒，property） |
| `end_time_ms` | `float` | 结束时间（毫秒，property） |
| `duration_ms` | `float` | 持续时间（毫秒，property） |
| `process` | `dict` | 进程信息（`upid`, `name`, `pid`） |
| `thread` | `dict` | 线程信息（`utid`, `name`, `tid`, `is_main_thread`） |
| `track` | `Track` | Track 对象 |
| `related` | `RelatedObjectsAccessor` | 关联对象访问器 |

### Slice 对象方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `get_process_name` | `get_process_name() -> str` | 获取进程名 |
| `get_thread_name` | `get_thread_name() -> str` | 获取线程名 |
| `get_track_name` | `get_track_name() -> str` | 获取 track 名 |
| `get_upid` | `get_upid() -> Optional[int]` | 获取进程 upid |
| `get_utid` | `get_utid() -> Optional[int]` | 获取线程 utid |
| `get_pid` | `get_pid() -> Optional[int]` | 获取进程 pid |
| `get_tid` | `get_tid() -> Optional[int]` | 获取线程 tid |
| `get_args` | `get_args() -> Optional[Dict]` | 获取完整 args 字典 |
| `get_arg` | `get_arg(key, default=None) -> Any` | 获取指定 args 值 |
| `arg` | `arg(key, default=None) -> Any` | `get_arg` 的别名 |
| `input_id` | `input_id(default=None) -> Optional[str]` | 从 name 提取 `id=0x...` |
| `frame_id` | `frame_id(default=None) -> Optional[int]` | 从 name 提取 `Choreographer#doFrame` 帧号 |
| `overlaps_with` | `overlaps_with(other: Slice) -> bool` | 是否与另一 slice 重叠 |
| `contains_timestamp` | `contains_timestamp(ts_ms: float) -> bool` | 是否包含指定时间戳（毫秒） |
| `contains` | `contains(ts_ns: int) -> bool` | 是否包含指定时间戳（纳秒） |
| `args` | `args(key=None, value=None) -> Any` | 获取 args 或按 args 过滤 |
| `args_filter` | `args_filter(**kwargs) -> List[Slice]` | 按 args 过滤并返回 slice 列表 |
| `parent` | `parent(level=1, **kwargs) -> SliceQueryBuilder` | 查找父节点 |
| `child` | `child(level=1, **kwargs) -> SliceQueryBuilder` | 查找子节点 |
| `descendants` | `descendants(**kwargs) -> SliceQueryBuilder` | 查找子孙节点 |
| `siblings` | `siblings(**kwargs) -> SliceQueryBuilder` | 查找同级节点 |
| `flow_out` | `flow_out(**kwargs) -> SliceQueryBuilder` | 查找 flow_out 关联 slice |
| `flow_in` | `flow_in(**kwargs) -> SliceQueryBuilder` | 查找 flow_in 关联 slice |
| `to_dict` | `to_dict() -> Dict` | 转为字典 |
| `from_dict` | `from_dict(data) -> Slice` | 从字典/Row 创建 Slice |

---

### 高级 Slice 定位语法

格式：`slice名称` + `|` + `进程名` + `||` + `线程名` + `|||` + `track名` + `||||` + `图层名` + `#索引`

| 分隔符 | 含义 |
|--------|------|
| 无 | 仅按 slice 名称匹配 |
| 单个 `|` | 指定进程 |
| 双 `||` | 指定线程 |
| 三 `|||` | 指定 track |
| 四 `||||` | 指定图层（Layer name args） |
| `#0` | 第一个匹配 |
| `#-1` | 最后一个匹配 |
| `#1` | 第二个匹配 |

**示例：**

```python
trace.slice(name="playing|system_server||Transition#0").first()
trace.slice().before("playing|system_server||Transition#0").all()
trace.slice().between("start|proc||thread", "end|proc||thread").all()
```

---

## 📁 其他 API 概览

| 入口 | 返回类型 | 说明 |
|------|----------|------|
| `trace.counter(**kwargs)` | `CounterQueryBuilder` | Counter 查询 |
| `trace.cpu_freq(**kwargs)` | `CpuFreqQueryBuilder` | CPU 频率查询 |
| `trace.cpu_usage(**kwargs)` | `CpuUsageQueryBuilder` | CPU 使用率查询 |
| `trace.metric(name=None, **kwargs)` | `List[str]` 或 `Dict` | Metric 查询 |

---

## 🧪 运行测试

```bash
uv run pytest tests/ -v
```

## 📚 相关文档

- **API 文档**: `Trace_API文档.md`
- **项目分析**: `项目分析报告.md`

## 📄 许可证

MIT License
