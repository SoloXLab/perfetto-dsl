# Perfetto DSL

一个为Perfetto trace文件提供链式DSL访问的Python库，支持懒加载、关联对象属性访问、强大的args参数过滤功能和高级slice定位语法。

## ✨ 主要特性

- **🔗 链式DSL**: 支持 `trace.slice(id=123).process(name="app").thread(name="main")` 的链式调用
- **⚡ 懒加载**: 查询只在需要时执行，提高性能
- **🔍 关联对象访问**: 支持 `slice.get_process_name()` 和 `slice.get_thread_name()` 的直接方法访问
- **📊 智能信息显示**: Slice对象自动显示process、thread、track名称和upid、utid、pid、tid等完整信息
- **📊 多种数据类型**: 支持 Slice、Counter、Track、Flow、CPU Usage、CPU Frequency 等Perfetto数据类型
- **🎯 高级Args参数过滤**: 支持通过slice的args参数进行精确和模糊匹配过滤
- **🎯 高级Slice定位语法**: 支持 `slice_name|process_name||thread_name|||track_name#index` 的精确slice定位
- **🔄 Flow关联查询**: 支持通过flow关系查找关联的slice
- **📈 聚合统计**: 支持count、max、min、avg、p90、p95等聚合方法
- **💻 CPU使用率分析**: 支持整体、进程、线程级别的CPU使用率查询，返回小数格式(1.0=100%)
- **⚡ CPU频率分析**: 支持CPU频点分析，包括进程/线程分组和自定义CPU核心分组
- **📊 JSON美化输出**: 所有字典格式数据都支持JSON美化输出
- **🧪 完整测试**: 包含全面的单元测试，覆盖所有功能

## 🚀 快速开始

### 安装

```bash
# 使用uv安装依赖
uv add perfetto

# 或者使用pip
pip install perfetto
```

### 基本使用

```python
from perfetto.dsl import Trace

# 打开trace文件
with Trace("trace_file.pftrace") as trace:
    # 基本查询
    slice_obj = trace.slice(id=123).first()
    
    # 链式查询
    slices = trace.slice(name="function_name").process(name="app_name").all()
    
    # 直接获取关联对象信息
    process_name = slice_obj.get_process_name()
    thread_tid = slice_obj.get_tid()
    track_name = slice_obj.get_track_name()
    
    print(f"Process: {process_name}")
    print(f"Thread TID: {thread_tid}")
    print(f"Track Name: {track_name}")
    
    # CPU使用率查询
    overall_usage = trace.cpu_usage()  # 整体CPU使用率 (小数格式)
    process_usage = trace.cpu_usage().process()  # 进程CPU使用率字典
    thread_usage = trace.cpu_usage().thread()  # 线程CPU使用率字典
    
    # CPU频率查询
    cpu_freq = trace.cpu_freq()  # CPU频点字典
    grouped_freq = trace.cpu_freq().group(little=[0,1,2,3], big=[4,5,6,7])  # CPU分组
```

## 📋 核心功能

### 1. CPU使用率查询 (CPU Usage)

```python
# 基本CPU使用率查询 - 返回小数格式 (1.0 = 100%)
overall_usage = trace.cpu_usage()  # 返回: 0.548378 (表示54.84%)

# 进程CPU使用率字典 - 按使用率从高到低排序
process_usage = trace.cpu_usage().process()
# 返回: {"process_name": 0.000745, ...} (JSON美化格式)

# 线程CPU使用率字典 - 按使用率从高到低排序  
thread_usage = trace.cpu_usage().thread()
# 返回: {"thread_name": 0.000367, ...} (JSON美化格式)

# 进程-线程嵌套字典 - 按名称排序
nested_usage = trace.cpu_usage().process().thread()
# 返回: {"process_name": {"thread_name": 0.000123, ...}, ...} (JSON美化格式)

# 过滤特定进程
specific_process = trace.cpu_usage().process("system_server")  # 返回: 0.054303

# 过滤特定线程
specific_thread = trace.cpu_usage().thread("binder:20820_7")  # 返回: 0.001234

# 过滤多个进程/线程
multiple_processes = trace.cpu_usage().process(["system_server", "surfaceflinger"])
multiple_threads = trace.cpu_usage().thread(["binder:20820_7", "RenderThread"])
```

### 2. CPU频率查询 (CPU Frequency)

```python
# 基本CPU频点字典 - 不同CPU核心上不同频点的总运行时长
cpu_freq = trace.cpu_freq()
# 返回: {"0": {"610000": 253911336, "820000": 295736654, ...}, ...}

# 进程分组 - 显示不同进程在不同CPU上的不同频点运行时长
process_freq = trace.cpu_freq().process()
# 返回: {"进程名": {"0": {"610000": 253911336, ...}, ...}, ...}

# 线程分组 - 显示不同线程在不同CPU上的不同频点运行时长
thread_freq = trace.cpu_freq().thread()
# 返回: {"线程名": {"0": {"610000": 253911336, ...}, ...}, ...}

# 进程-线程嵌套分组
nested_freq = trace.cpu_freq().process().thread()
# 返回: {"进程名": {"线程名": {"0": {"610000": 253911336, ...}, ...}, ...}, ...}

# CPU分组功能 - 将指定的CPU核心按组名分组合并
grouped_freq = trace.cpu_freq().group(little=[0,1,2,3], big=[4,5,6,7])
# 返回: {"little": {"610000": 1015645344, ...}, "big": {"1065000": 1674524576, ...}}

# 自定义分组
custom_grouped = trace.cpu_freq().group(
    cluster1=[0, 1], 
    cluster2=[2, 3], 
    cluster3=[4, 5], 
    cluster4=[6, 7, 8]
)

# 分组与其他功能结合
process_grouped = trace.cpu_freq().process().group(little=[0,1,2,3], big=[4,5,6,7])
thread_grouped = trace.cpu_freq().thread().group(little=[0,1,2,3], big=[4,5,6,7])
nested_grouped = trace.cpu_freq().process().thread().group(little=[0,1,2,3], big=[4,5,6,7])

# 过滤特定进程/线程
filtered_process = trace.cpu_freq().process("system_server")
filtered_thread = trace.cpu_freq().thread("binder:20820_7")
```

### 3. Slice查询

```python
# 基本slice查询
slices = trace.slice(id=123).all()
slices = trace.slice(name="function_name").all()
slices = trace.slice(cat="category").all()

# 链式查询
slices = trace.slice().process(name="app").thread(name="main").all()

# 模糊匹配
slices = trace.slice(name="%doFrame%").all()  # 包含"doFrame"的slice

# 智能信息显示 - Slice对象自动显示完整信息
slice_obj = trace.slice(id=123).first()
print(slice_obj)  # 输出: Slice(id=123, name='function_name', ts=100.00ms, duration=5.00ms, process='app_name', track='track_name', pid=12705, tid=12705)
```

### 4. 高级Slice定位语法 🆕

```python
# 高级语法: slice_name|process_name||thread_name|||track_name||||layer_name#index
# 使用 | 分隔slice名称和进程名
# 使用 || 分隔进程名和线程名  
# 使用 ||| 分隔线程名和track名
# 使用 |||| 分隔track名和图层名
# 使用 # 指定索引 (0=第一个, -1=最后一个, 1=第二个, 2=第三个...)

# 基本用法
slices = trace.slice(name="906975|system_server").all()  # 在system_server进程中的906975 slice

# 指定线程
slices = trace.slice(name="playing|system_server||Transition").all()  # 在system_server进程Transition线程中的playing slice

# 指定track
slices = trace.slice(name="906975|||Expected Timeline").all()  # 在Expected Timeline track中的906975 slice

# 指定图层
slices = trace.slice(name="906975||||transition-leash").all()  # 在transition-leash图层中的906975 slice

# 完整语法
slices = trace.slice(name="playing|system_server||Transition|||Expected Timeline||||transition-leash").all()

# 指定索引
slices = trace.slice(name="playing|system_server||Transition|||Expected Timeline#0").all()  # 第一个匹配的slice
slices = trace.slice(name="playing|system_server||Transition|||Expected Timeline#-1").all()  # 最后一个匹配的slice
slices = trace.slice(name="906975||||transition-leash#0").all()  # 第一个匹配的图层slice

# 在时间范围查询中使用
slices = trace.slice().before("playing|system_server||Transition#0").all()
slices = trace.slice().after("906975|||Expected Timeline#1").all()
slices = trace.slice().before("906975||||transition-leash#0").all()  # 使用图层语法
slices = trace.slice().between("start_slice|process||thread", "end_slice|process||thread").all()
```

### 5. Args参数过滤 🆕

```python
# 获取slice的args参数
slice_obj = trace.slice(id=123).first()
args_dict = slice_obj.args()  # 返回完整的args字典
surface_token = slice_obj.args("Surface frame token")  # 获取指定key的值

# 使用args进行过滤 (Slice方法)
filtered_slices = slice_obj.args("Surface frame token", 906975)  # 返回匹配的slice列表

# 使用args进行过滤 (QueryBuilder方法)
slices = trace.slice().args("Surface frame token", 906975).all()

# 字符串模糊匹配
slices = trace.slice().args("Layer name", "Surface").all()  # 包含"Surface"的Layer name
slices = trace.slice().args("Layer name", "TX").all()       # 包含"TX"的Layer name

# 数字精确匹配
slices = trace.slice().args("Surface frame token", 906975).all()

# 组合args过滤
slices = (trace.slice()
          .args("Surface frame token", 906975)
          .args("Layer name", "Surface")
          .all())

# 在时间范围查询中使用args过滤
slices = (trace.slice()
          .between("playing|system_server|||Transition#0")
          .args("Layer name", "transition-leash")
          .all())
```

### 6. 多个Slice的Args处理 🆕

```python
# 当QueryBuilder返回多个slice时，args()方法的行为：

# 1. args() - 返回所有slice的args字典列表
args_list = trace.slice().args("Surface frame token", 906975).args()
# 返回: [{'Surface frame token': 906975, 'Layer name': '...'}, {...}, ...]

# 2. args(key) - 返回所有slice对应key的值列表
surface_tokens = trace.slice().args("Surface frame token", 906975).args("Surface frame token")
# 返回: [906975, 906975, 906975, 906975]

layer_names = trace.slice().args("Surface frame token", 906975).args("Layer name")
# 返回: ['TX - Surface(name=Task=1)/@0x4e06afd_transition-leash#1076', ...]

# 3. args(key, value) - 进行过滤，返回匹配的slice列表
filtered_slices = trace.slice().args("Surface frame token", 906975).args("Layer name", "transition-leash")
# 返回: 匹配条件的slice列表

# 实际使用示例
slice_result = trace.slice().args("Surface frame token", 906975)
print(f"找到的slice数量: {len(list(slice_result))}")

# 获取所有slice的args信息
args_list = trace.slice().args("Surface frame token", 906975).args()
for i, args_dict in enumerate(args_list):
    print(f"Slice {i+1} args: {args_dict}")

# 获取特定key的所有值
layer_names = trace.slice().args("Surface frame token", 906975).args("Layer name")
print(f"所有Layer name: {layer_names}")

# 对args值进行统计操作
surface_tokens = trace.slice(name="|launcher|||Actual Timeline").args("Surface frame token")
print(f"总数: {surface_tokens.count()}")
print(f"最大值: {surface_tokens.max()}")
print(f"最小值: {surface_tokens.min()}")
print(f"平均值: {surface_tokens.avg()}")
print(f"总和: {surface_tokens.sum()}")
print(f"唯一值数量: {surface_tokens.unique_count()}")
print(f"唯一值列表: {surface_tokens.unique()}")
```

### 7. Args值统计功能 🆕

```python
# 获取args值并进行各种统计操作
surface_tokens = trace.slice(name="|launcher|||Actual Timeline").args("Surface frame token")

# 基本统计
print(f"总数: {surface_tokens.count()}")                    # 包括None值
print(f"非空值数量: {surface_tokens.count_non_null()}")      # 排除None值

# 数值统计（仅对数值类型有效）
print(f"最大值: {surface_tokens.max()}")
print(f"最小值: {surface_tokens.min()}")
print(f"平均值: {surface_tokens.avg()}")
print(f"总和: {surface_tokens.sum()}")

# 唯一值统计
print(f"唯一值数量: {surface_tokens.unique_count()}")
print(f"唯一值列表: {surface_tokens.unique()}")

# 字符串类型args的统计
layer_names = trace.slice(name="|launcher|||Actual Timeline").args("Layer name")
print(f"Layer name总数: {layer_names.count()}")
print(f"Layer name唯一值数量: {layer_names.unique_count()}")
print(f"Layer name唯一值: {layer_names.unique()}")

# 支持索引访问和迭代
print(f"第一个值: {surface_tokens[0]}")
print(f"最后一个值: {surface_tokens[-1]}")

for i, value in enumerate(surface_tokens):
    if i >= 5:  # 只显示前5个
        break
    print(f"  {i}: {value}")
```

### 8. Flow关联查询

```python
# 查找通过flow关联的slice_out
flow_out_slices = trace.slice(id=123).flow_out().all()

# 查找通过flow关联的slice_in
flow_in_slices = trace.slice(id=123).flow_in().all()

# 链式flow查询
result = (trace
          .slice(name="%binder%")
          .process(name="%system%")
          .first()
          .flow_out()
          .process(name="%surfaceflinger%")
          .first())
```

### 9. 时间范围查询

```python
# 在指定slice之后
slices = trace.slice().after(some_slice).all()

# 在指定slice之前
slices = trace.slice().before(some_slice).all()

# 在时间范围内
slices = trace.slice().between(start_slice, end_slice).all()
slices = trace.slice().between(single_slice).all()  # 使用单个slice的时间范围

# 使用高级语法进行时间范围查询
slices = trace.slice().before("playing|system_server||Transition#0").all()
slices = trace.slice().after("906975|||Expected Timeline#1").all()
```

### 10. 聚合统计

```python
# 计数
count = trace.slice().process(name="app").count()

# 聚合统计
max_duration = trace.slice().max('duration')
min_duration = trace.slice().min('duration')
avg_duration = trace.slice().avg('duration')
p90_duration = trace.slice().p90('duration')
p95_duration = trace.slice().p95('duration')
```

### 11. 关联对象访问

```python
slice_obj = trace.slice(id=123).first()

# 直接获取进程信息
process_name = slice_obj.get_process_name()
process_pid = slice_obj.get_pid()
process_upid = slice_obj.get_upid()

# 直接获取线程信息
thread_name = slice_obj.get_thread_name()
thread_tid = slice_obj.get_tid()
thread_utid = slice_obj.get_utid()

# 直接获取track信息
track_name = slice_obj.get_track_name()

# 或者通过属性访问（返回字典）
process_info = slice_obj.process
thread_info = slice_obj.thread
track_info = slice_obj.track
```

## 🎯 高级用法

### 复杂链式查询

```python
# 复杂的链式查询示例
result = (trace
          .slice(name="%doFrame%")
          .process(name="com.google.android.apps.nexuslauncher")
          .thread(main=True)
          .after(playing_slice)
          .parent(level=1)
          .first()
          .flow_out()
          .process(name="%surfaceflinger%")
          .first())
```

### 高级Slice定位和Args过滤组合

```python
# 使用高级语法定位slice并进行args过滤
slices = (trace.slice()
          .between("playing|system_server|||Transition#0", "906975|||Expected Timeline#1")
          .args("Layer name", "transition-leash")
          .all())

# 复杂的组合查询
result = (trace.slice()
          .name("906975|launcher|||Actual Timeline")
          .between("playing|system_server|||Transition#0")
          .args("Layer name", "transition-leash")
          .all())
```

### Args参数高级过滤

```python
# 多种args参数组合
slices = trace.slice().args(
    "Layer name", "Surface",
    "Present type", "On-time Present"
).all()

# 获取特定slice的args并过滤
slice_obj = trace.slice(id=41300).first()
print("Args:", slice_obj.args())

# 通过args过滤并获取详细信息
for slice_obj in trace.slice().args("Layer name", "eash#1076"):
    print(f"Slice: {slice_obj}")
    print(f"Args: {slice_obj.args()}")
```

### 时间范围高级查询

```python
# 在特定时间范围内的聚合统计
query = trace.slice().process(name="app").between(start_slice, end_slice)
count = query.count()
avg_duration = query.avg('duration')
max_duration = query.max('duration')
```

## 📁 项目结构

```
perfetto-dsl/
├── perfetto/              # 主包目录
│   ├── __init__.py       # 包初始化文件
│   └── dsl/              # DSL子包
│       ├── __init__.py   # DSL包初始化
│       ├── trace.py      # 主入口类
│       ├── slice_query_builder.py # 查询构建器（包含Slice、Track、Flow、RelatedObjectsAccessor）
│       ├── counter_query_builder.py # Counter数据类和查询构建器
│       ├── cpu_freq_query_builder.py # CPU频率查询构建器
│       └── cpu_usage_query_builder.py # CPU使用率查询构建器
├── tests/                # 测试文件
├── pyproject.toml        # 项目配置
└── README.md            # 项目说明
```

## 🧪 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_basic_functionality.py -v
```

## 🔧 技术特点

- **基于Perfetto官方文档**: 严格按照Perfetto SQL表结构设计
- **双重查询策略**: 支持通过process_track和thread_track两种方式获取进程信息
- **智能信息显示**: Slice对象自动显示所有可用的关联信息（process、thread、track、pid、tid）
- **缓存机制**: 避免重复查询相同数据
- **错误处理**: 优雅处理数据不存在的情况，过滤'None'字符串
- **类型安全**: 完整的类型注解
- **高级Args参数支持**: 完整的args参数查询和过滤功能
- **高级Slice定位语法**: 支持精确的slice定位，避免多slice匹配问题
- **模糊匹配**: 支持SQL LIKE操作符的模糊匹配
- **多JOIN支持**: 支持多个args参数的组合查询
- **懒加载**: QueryBuilder支持直接打印，自动执行查询并显示结果
- **符号安全**: 使用安全的符号（|、||、|||、#）避免与slice名称冲突

## 📝 使用示例

查看 `main.py` 文件获取完整的使用示例，包括：

- 基本slice查询
- 高级slice定位语法
- Args参数过滤
- 组合过滤查询
- Flow关联查询
- 聚合统计
- CPU使用率分析
- CPU频率分析
- CPU分组功能

### 完整示例

```python
from perfetto.dsl import Trace

with Trace("trace_file.pftrace") as trace:
    # 使用高级语法和args过滤的组合查询
    slice_result = (trace.slice(name="906975|launcher|||Actual Timeline")
                   .between("playing|system_server|||Transition#0")
                   .args("Layer name", "transition-leash"))
    
    print(slice_result)
    print([s.args() for s in slice_result])
    
    # 输出示例:
    # Slice(id=40635, name='906975', ts=341078042.66ms, duration=16.60ms, process='com.google.android.apps.nexuslauncher', track='Expected Timeline', pid=12705)
    # [{'Surface frame token': 906975, 'Display frame token': 907003, 'Layer name': 'TX - Surface(name=Task=Task=1)/@0x4e06afd_transition-leash#1076'}]
    
    # CPU使用率分析示例
    print("\n=== CPU使用率分析 ===")
    overall_usage = trace.cpu_usage()
    print(f"整体CPU使用率: {overall_usage} ({overall_usage*100:.2f}%)")
    
    process_usage = trace.cpu_usage().process()
    print("前3个进程的CPU使用率:")
    import json
    process_data = json.loads(str(process_usage))
    for i, (process_name, usage) in enumerate(process_data.items()):
        if i >= 3:
            break
        print(f"  {process_name}: {usage:.6f} ({usage*100:.2f}%)")
    
    # CPU频率分析示例
    print("\n=== CPU频率分析 ===")
    cpu_freq = trace.cpu_freq()
    print("CPU频点分布:")
    freq_data = json.loads(str(cpu_freq))
    for cpu_id, freq_info in list(freq_data.items())[:3]:  # 显示前3个CPU
        print(f"  CPU {cpu_id}: {len(freq_info)} 个频点")
        for freq_mhz, duration in list(freq_info.items())[:2]:  # 显示前2个频点
            print(f"    {freq_mhz}MHz: {duration}ns ({duration/1000000:.2f}ms)")
    
    # CPU分组分析示例
    print("\n=== CPU分组分析 ===")
    grouped_freq = trace.cpu_freq().group(little=[0,1,2,3], big=[4,5,6,7])
    grouped_data = json.loads(str(grouped_freq))
    for group_name, freq_info in grouped_data.items():
        total_duration = sum(freq_info.values())
        print(f"  {group_name} 组: {len(freq_info)} 个频点, 总时长: {total_duration/1000000:.2f}ms")
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License