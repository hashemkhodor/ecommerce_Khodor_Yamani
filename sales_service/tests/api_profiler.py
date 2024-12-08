import asyncio
import cProfile
from pstats import Stats

from app.models import Purchase
from app.service import get_purchases, process_purchase
from line_profiler import LineProfiler
from memory_profiler import profile


# Profiling fetch_all_purchases
async def fetch_all_purchases_profile():
    return get_purchases()


# Profiling process_purchase
async def process_purchase_profile():
    customer_username = "testuser"
    good_id = 1
    return process_purchase(customer_username, good_id)


# cProfile Function
def profile_cprofile(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(func(*args, **kwargs))  # Async support
    profiler.disable()
    stats = Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("time")
    stats.print_stats()


# Synchronous Wrappers for LineProfiler
def mock_fetch_all_purchases_sync():
    asyncio.run(fetch_all_purchases_profile())


def mock_process_purchase_sync():
    asyncio.run(process_purchase_profile())


# LineProfiler for All Functions
def line_profile():
    profiler = LineProfiler()
    profiler.add_function(mock_fetch_all_purchases_sync)
    profiler.add_function(mock_process_purchase_sync)
    profiler.run("mock_fetch_all_purchases_sync()")
    profiler.run("mock_process_purchase_sync()")
    profiler.print_stats()


# Memory Profiling for All Functions
@profile
async def memory_profile():
    await fetch_all_purchases_profile()
    await process_purchase_profile()


# Main Execution
if __name__ == "__main__":
    print("Profiling with cProfile:")
    profile_cprofile(fetch_all_purchases_profile)
    profile_cprofile(process_purchase_profile)

    print("\nProfiling line-by-line:")
    line_profile()

    print("\nProfiling memory usage:")
    asyncio.run(memory_profile())
