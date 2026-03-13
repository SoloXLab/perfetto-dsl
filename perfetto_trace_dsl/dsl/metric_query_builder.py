from typing import Dict, Any, List, Union
from perfetto.trace_processor import TraceProcessor

class MetricQueryBuilder:
    """Metric查询构建器，用于处理Perfetto metrics"""

    def __init__(self, trace_processor: TraceProcessor, **kwargs):
        self.trace_processor = trace_processor
        self.kwargs = kwargs

    def list_all(self) -> List[str]:
        """
        列出所有可用的metrics
        
        Returns:
            List[str]: 所有可用的metrics名称列表
        """
        try:
            result = self.trace_processor.metric(metrics=[])
            # TraceMetrics 对象的属性名就是可用的 metrics
            # 过滤掉以 _ 开头的私有属性、特殊方法和非 metric 属性
            exclude_attrs = {'DESCRIPTOR', 'Extensions', 'ByteSize', 'Clear', 'ClearExtension', 
                           'ClearField', 'CopyFrom', 'DiscardUnknownFields', 'FindInitializationErrors',
                           'FromString', 'HasExtension', 'HasField', 'IsInitialized', 'ListFields',
                           'MergeFrom', 'MergeFromString', 'ParseFromString', 'SerializePartialToString',
                           'SerializeToString', 'SetInParent', 'UnknownFields', 'WhichOneof'}
            
            metrics = []
            for attr_name in dir(result):
                if (not attr_name.startswith('_') and 
                    not callable(getattr(result, attr_name)) and
                    attr_name not in exclude_attrs):
                    metrics.append(attr_name)
            return sorted(metrics)
        except Exception as e:
            raise RuntimeError(f"Failed to list metrics: {e}")

    def execute(self, metric_name: str) -> Dict[str, Any]:
        """
        执行指定的metric
        
        Args:
            metric_name: 要执行的metric名称
            
        Returns:
            Dict[str, Any]: metric结果字典
        """
        try:
            result = self.trace_processor.metric(metrics=[metric_name])
            # 检查是否有指定的 metric 属性
            if hasattr(result, metric_name):
                metric_data = getattr(result, metric_name)
                # 将 metric 数据转换为字典格式
                return {metric_name: metric_data}
            else:
                # 如果没有找到指定的 metric，返回空字典
                return {}
        except Exception as e:
            raise RuntimeError(f"Failed to run metric '{metric_name}': {e}")

    def __call__(self, metric_name: str = None) -> Union[List[str], Dict[str, Any]]:
        """
        支持直接调用实例来列出或执行metric
        
        Args:
            metric_name: metric名称，如果不提供则返回所有可用的metrics列表
            
        Returns:
            如果提供了metric_name，返回metric结果字典
            如果没有提供metric_name，返回所有可用的metrics字符串列表
        """
        if metric_name is None:
            return self.list_all()
        else:
            return self.execute(metric_name)