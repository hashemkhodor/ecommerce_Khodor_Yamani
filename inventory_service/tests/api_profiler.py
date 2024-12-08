import asyncio
from line_profiler import LineProfiler
from memory_profiler import profile
import cProfile
from pstats import Stats
from app.service import add_good, update_good, get_good, deduct_good
from app.models import Good, GoodUpdate


# Profiling add_good
async def add_good_profile():
    test_good = Good(
        name="Test Item",
        category="electronics",
        price=99.99,
        description="A test item for profiling.",
        count=10,
    )
    return add_good(test_good)


# Profiling update_good
async def update_good_profile():
    test_good_update = GoodUpdate(name="Updated Item", count=20)
    return update_good(1, test_good_update)  # Assuming ID 1 exists


# Profiling get_good
async def get_good_profile():
    return get_good(1)  # Assuming ID 1 exists


# Profiling deduct_good
async def deduct_good_profile():
    return deduct_good(1)  # Assuming ID 1 exists


# Function for cProfile
def profile_cprofile(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(func(*args, **kwargs))  # Async support
    profiler.disable()
    stats = Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('time')
    stats.print_stats()


# Synchronous Wrappers for LineProfiler
def mock_add_good_sync():
    asyncio.run(add_good_profile())


def mock_update_good_sync():
    asyncio.run(update_good_profile())


def mock_get_good_sync():
    asyncio.run(get_good_profile())


def mock_deduct_good_sync():
    asyncio.run(deduct_good_profile())


# LineProfiler for All Functions
def line_profile():
    profiler = LineProfiler()
    profiler.add_function(mock_add_good_sync)
    profiler.add_function(mock_update_good_sync)
    profiler.add_function(mock_get_good_sync)
    profiler.add_function(mock_deduct_good_sync)
    profiler.run("mock_add_good_sync()")
    profiler.run("mock_update_good_sync()")
    profiler.run("mock_get_good_sync()")
    profiler.run("mock_deduct_good_sync()")
    profiler.print_stats()


# Memory Profiling for All Functions
@profile
async def memory_profile():
    await add_good_profile()
    await update_good_profile()
    await get_good_profile()
    await deduct_good_profile()


# Main Execution
if __name__ == "__main__":
    print("Profiling with cProfile:")
    profile_cprofile(add_good_profile)
    profile_cprofile(update_good_profile)
    profile_cprofile(get_good_profile)
    profile_cprofile(deduct_good_profile)

    print("\nProfiling line-by-line:")
    line_profile()

    print("\nProfiling memory usage:")
    asyncio.run(memory_profile())
