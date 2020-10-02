from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
import os

class MetricLogger:
    def __init__(self, metric_name:str, custom_dimension_keys:list=[]):
        self.custom_dimension_keys = custom_dimension_keys
        stats = stats_module.stats
        view_manager = stats.view_manager
        stats_recorder = stats.stats_recorder
        self.metric_measure_module = measure_module.MeasureFloat("Metric", "", "")

        request_view = view_module.View(metric_name, "",
                                        self.custom_dimension_keys,
                                        self.metric_measure_module,
                                        aggregation_module.LastValueAggregation())

        exporter = metrics_exporter.new_metrics_exporter(connection_string=f'InstrumentationKey={os.environ.get("APPINSIGHTS_INSTRUMENTATION_KEY")}')
        
        view_manager.register_exporter(exporter)

        view_manager.register_view(request_view)
        self.mmap = stats_recorder.new_measurement_map()
        self.tmap = tag_map_module.TagMap()

    def insert_customdimension(self, key: str, value: str):
        if key not in self.custom_dimension_keys:
            self.custom_dimension_keys.append(key)
        
        self.tmap.insert(key, value)
    
    def set_customdimension(self, custom_dimension: dict):
        for key, value in custom_dimension.items():
            self.insert_customdimension(key, str(value))

    def set_metric_value(self, value:float):
        self.mmap.measure_float_put(self.metric_measure_module, value)
        self.mmap.record(self.tmap)