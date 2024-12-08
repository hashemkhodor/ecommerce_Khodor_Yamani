import asyncio
from line_profiler import LineProfiler
from memory_profiler import profile
import cProfile
from pstats import Stats
from app.main import (
    submit_review,
    update_review,
    delete_review,
    get_item_review,
    get_customer_review,
    login,
)
from app.schemas import PostReviewRequest, PutReviewRequest, LoginRequest


# Profiling submit_review
async def submit_review_profile():
    review_data = PostReviewRequest(
        customer_id="testuser",
        item_id=1,
        rating=5,
        comment="Excellent product!",
    )
    return await submit_review(review_data)


# Profiling update_review
async def update_review_profile():
    update_data = PutReviewRequest(
        customer_id="testuser",
        item_id=1,
        rating=4,
        comment="Updated my review: great product!",
    )
    return await update_review(update_data)


# Profiling delete_review
async def delete_review_profile():
    return await delete_review(customer_id="testuser", item_id=1)


# Profiling get_item_review
async def get_item_review_profile():
    return await get_item_review(item_id=1)


# Profiling get_customer_review
async def get_customer_review_profile():
    return await get_customer_review(customer_id="testuser")


# Profiling login
async def login_profile():
    credentials = LoginRequest(username="angelvaughan", password="+PNLtQ^Y^5")
    return await login(credentials)


# cProfile Function
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
def mock_submit_review_sync():
    asyncio.run(submit_review_profile())


def mock_update_review_sync():
    asyncio.run(update_review_profile())


def mock_delete_review_sync():
    asyncio.run(delete_review_profile())


def mock_get_item_review_sync():
    asyncio.run(get_item_review_profile())


def mock_get_customer_review_sync():
    asyncio.run(get_customer_review_profile())


def mock_login_sync():
    asyncio.run(login_profile())


# LineProfiler for All Functions
def line_profile():
    profiler = LineProfiler()
    profiler.add_function(mock_submit_review_sync)
    profiler.add_function(mock_update_review_sync)
    profiler.add_function(mock_delete_review_sync)
    profiler.add_function(mock_get_item_review_sync)
    profiler.add_function(mock_get_customer_review_sync)
    profiler.add_function(mock_login_sync)
    profiler.run("mock_submit_review_sync()")
    profiler.run("mock_update_review_sync()")
    profiler.run("mock_delete_review_sync()")
    profiler.run("mock_get_item_review_sync()")
    profiler.run("mock_get_customer_review_sync()")
    profiler.run("mock_login_sync()")
    profiler.print_stats()


# Memory Profiling for All Functions
@profile
async def memory_profile():
    await submit_review_profile()
    await update_review_profile()
    await delete_review_profile()
    await get_item_review_profile()
    await get_customer_review_profile()
    await login_profile()


# Main Execution
if __name__ == "__main__":
    print("Profiling with cProfile:")
    profile_cprofile(submit_review_profile)
    profile_cprofile(update_review_profile)
    profile_cprofile(delete_review_profile)
    profile_cprofile(get_item_review_profile)
    profile_cprofile(get_customer_review_profile)
    profile_cprofile(login_profile)

    print("\nProfiling line-by-line:")
    line_profile()

    print("\nProfiling memory usage:")
    asyncio.run(memory_profile())
