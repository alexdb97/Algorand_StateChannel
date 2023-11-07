import functools
import time


def bench(func):
    
    @functools.wraps(func)
    def wrapper_brench(*args, **kwargs):
        start_time = time.perf_counter()         
        res1,res2 = func(*args)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        return [res1,run_time,res2]
    
    return wrapper_brench