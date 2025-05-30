"""
Performance Monitor for Media Plan to Raw Data Automation
Tracks processing times, memory usage, and provides progress indicators
"""

import time
import psutil
import os
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import logging
from contextlib import contextmanager
from tqdm import tqdm
import pandas as pd


class PerformanceMonitor:
    """Monitor and report on processing performance"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
        self.logger = logging.getLogger(__name__)
        
    @contextmanager
    def track_operation(self, operation_name: str, total_items: Optional[int] = None):
        """Context manager to track operation performance"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        # Create progress bar if total items provided
        progress_bar = None
        if total_items:
            progress_bar = tqdm(total=total_items, desc=operation_name, unit='items')
            
        try:
            # Yield progress updater function
            def update_progress(n=1):
                if progress_bar:
                    progress_bar.update(n)
                    
            yield update_progress
            
        finally:
            # Calculate metrics
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            duration = end_time - start_time
            memory_delta = end_memory - start_memory
            
            # Store metrics
            self.metrics[operation_name] = {
                'duration_seconds': duration,
                'memory_delta_mb': memory_delta,
                'items_processed': total_items,
                'items_per_second': total_items / duration if total_items and duration > 0 else None,
                'timestamp': datetime.now().isoformat()
            }
            
            # Close progress bar
            if progress_bar:
                progress_bar.close()
                
            # Log summary
            self.logger.info(
                f"⏱️ {operation_name}: {duration:.2f}s, "
                f"Memory: {memory_delta:+.1f}MB"
                + (f", Speed: {total_items/duration:.0f} items/s" if total_items else "")
            )
            
    def _get_memory_usage(self) -> float:
        """Get current process memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
        
    def track_dataframe_operation(self, df: pd.DataFrame, operation: str):
        """Track operations on dataframes with size awareness"""
        rows, cols = df.shape
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        
        self.logger.info(
            f"📊 {operation}: {rows:,} rows × {cols} columns, "
            f"Memory: {memory_usage:.1f}MB"
        )
        
        return {
            'rows': rows,
            'columns': cols,
            'memory_mb': memory_usage
        }
        
    def create_performance_summary(self) -> str:
        """Create a summary of all tracked operations"""
        lines = [
            "=" * 60,
            "PERFORMANCE SUMMARY",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            ""
        ]
        
        total_duration = 0
        total_memory = 0
        
        for operation, metrics in self.metrics.items():
            duration = metrics['duration_seconds']
            memory = metrics.get('memory_delta_mb', 0)
            total_duration += duration
            total_memory += abs(memory)
            
            lines.append(f"{operation}:")
            lines.append(f"  Duration: {duration:.2f}s")
            
            if metrics.get('items_processed'):
                lines.append(f"  Items: {metrics['items_processed']:,}")
                if metrics.get('items_per_second'):
                    lines.append(f"  Speed: {metrics['items_per_second']:.0f} items/s")
                    
            lines.append(f"  Memory: {memory:+.1f}MB")
            lines.append("")
            
        lines.extend([
            "-" * 60,
            f"Total Duration: {total_duration:.2f}s",
            f"Peak Memory Delta: {total_memory:.1f}MB",
            ""
        ])
        
        return "\n".join(lines)
        

class ProgressTracker:
    """Enhanced progress tracking for long operations"""
    
    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = time.time()
        self.step_times = []
        
        # Create main progress bar
        self.pbar = tqdm(
            total=total_steps,
            desc=description,
            unit='step',
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
        )
        
    def update(self, step_description: str = None, increment: int = 1):
        """Update progress with optional step description"""
        if step_description:
            self.pbar.set_postfix_str(step_description)
            
        self.pbar.update(increment)
        self.current_step += increment
        self.step_times.append(time.time())
        
    def close(self):
        """Close progress bar and show summary"""
        self.pbar.close()
        
        duration = time.time() - self.start_time
        avg_time_per_step = duration / self.current_step if self.current_step > 0 else 0
        
        print(f"\n✅ {self.description} completed in {duration:.1f}s")
        print(f"   Average time per step: {avg_time_per_step:.2f}s")
        

def add_progress_tracking(func: Callable) -> Callable:
    """Decorator to add progress tracking to any function"""
    def wrapper(*args, **kwargs):
        # Try to determine total items from args
        total_items = None
        if args and hasattr(args[0], '__len__'):
            total_items = len(args[0])
        elif 'data' in kwargs and hasattr(kwargs['data'], '__len__'):
            total_items = len(kwargs['data'])
            
        func_name = func.__name__
        monitor = PerformanceMonitor()
        
        with monitor.track_operation(func_name, total_items) as update_progress:
            # Pass progress updater to function if it accepts it
            if 'progress_callback' in func.__code__.co_varnames:
                kwargs['progress_callback'] = update_progress
                
            result = func(*args, **kwargs)
            
        return result
        
    return wrapper


# Integration helper for existing code
def integrate_progress_monitoring(mapper_instance):
    """Add progress monitoring to existing mapper instance"""
    monitor = PerformanceMonitor()
    
    # Track main operations
    original_map_data = mapper_instance.map_data
    
    def enhanced_map_data(combined_file: str, template_file: str, output_file: str) -> Dict[str, Any]:
        progress = ProgressTracker(6, "Mapping data to template")
        
        try:
            progress.update("Loading data files")
            start_result = original_map_data.__wrapped__(
                mapper_instance, combined_file, template_file, output_file
            )
            
            # The actual implementation with progress updates
            # Since we can't modify the internals, we'll wrap the whole operation
            with monitor.track_operation("Total Mapping Process"):
                result = original_map_data(combined_file, template_file, output_file)
                
        finally:
            progress.close()
            
        # Add performance metrics to result
        if isinstance(result, dict):
            result['performance_metrics'] = monitor.metrics
            
        return result
        
    mapper_instance.map_data = enhanced_map_data
    mapper_instance.performance_monitor = monitor
    
    return mapper_instance