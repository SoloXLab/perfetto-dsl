from .slice_query_builder import SliceQueryBuilder
from .counter_query_builder import CounterQueryBuilder
from .cpu_freq_query_builder import CpuFreqQueryBuilder
from .cpu_usage_query_builder import CpuUsageQueryBuilder
from .metric_query_builder import MetricQueryBuilder
from perfetto.trace_processor import TraceProcessor


class Trace:
    """Trace文件的主要入口点"""
    
    def __init__(self, trace_file: str):
        self.trace_processor = TraceProcessor(trace=trace_file)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.trace_processor.close()
    
    def slice(self, **kwargs) -> SliceQueryBuilder:
        """开始slice查询"""
        builder = SliceQueryBuilder(self.trace_processor)
        return builder.slice(**kwargs)
    
    def counter(self, **kwargs) -> CounterQueryBuilder:
        """开始counter查询"""
        return CounterQueryBuilder(self.trace_processor, **kwargs)
    
    def cpu_freq(self, **kwargs) -> CpuFreqQueryBuilder:
        """开始CPU频率查询"""
        return CpuFreqQueryBuilder(self.trace_processor, **kwargs)
    
    def cpu_usage(self, **kwargs) -> CpuUsageQueryBuilder:
        """开始CPU使用率查询"""
        return CpuUsageQueryBuilder(self.trace_processor, **kwargs)
    
    def metric(self, metric_name: str = None, **kwargs):
        """
        开始metric查询
        
        Args:
            metric_name: metric名称，如果不提供则返回所有可用的metrics列表
            **kwargs: 传递给metric的额外参数
            
        Returns:
            如果提供了metric_name，返回metric结果字典
            如果没有提供metric_name，返回所有可用的metrics字符串列表
        """
        builder = MetricQueryBuilder(self.trace_processor, **kwargs)
        if metric_name is None:
            return builder.list_all()
        else:
            return builder.execute(metric_name)
