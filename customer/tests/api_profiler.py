import asyncio
import cProfile
from pstats import Stats

from app.main import (
    charge_wallet,
    deduct_wallet,
    delete_customer,
    get_all_customers,
    get_customer,
    register_customer,
    update_customer,
)
from line_profiler import LineProfiler
from memory_profiler import profile


# Profiling register_customer
async def register_customer_profile():
    from app.schemas import CustomerRegisterRequestSchema

    test_customer = CustomerRegisterRequestSchema(
        name="Test User",
        username="testuser10",
        password="test123",
        age=25,
        address="123 Test Street",
        gender=True,
        marital_status="single",
    )
    return await register_customer(test_customer)


# Profiling delete_customer
async def delete_customer_profile():
    return await delete_customer("testuser10")


# Profiling update_customer
async def update_customer_profile():
    from app.schemas import CustomerUpdateSchema

    update_data = CustomerUpdateSchema(name="Updated Name")
    return await update_customer("testuser10", update_data)


# Profiling get_all_customers
async def get_all_customers_profile():
    return await get_all_customers()


# Profiling get_customer
async def get_customer_profile():
    return await get_customer("testuser10")


# Profiling charge_wallet
async def charge_wallet_profile():
    return await charge_wallet("testuser10", amount=100.0)


# Profiling deduct_wallet
async def deduct_wallet_profile():
    return await deduct_wallet("testuser10", amount=50.0)


# Function for cProfile
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
def mock_register_customer_sync():
    asyncio.run(register_customer_profile())


def mock_delete_customer_sync():
    asyncio.run(delete_customer_profile())


def mock_update_customer_sync():
    asyncio.run(update_customer_profile())


def mock_get_all_customers_sync():
    asyncio.run(get_all_customers_profile())


def mock_get_customer_sync():
    asyncio.run(get_customer_profile())


def mock_charge_wallet_sync():
    asyncio.run(charge_wallet_profile())


def mock_deduct_wallet_sync():
    asyncio.run(deduct_wallet_profile())


# LineProfiler for All Functions
def line_profile():
    profiler = LineProfiler()
    profiler.add_function(mock_register_customer_sync)
    profiler.add_function(mock_delete_customer_sync)
    profiler.add_function(mock_update_customer_sync)
    profiler.add_function(mock_get_all_customers_sync)
    profiler.add_function(mock_get_customer_sync)
    profiler.add_function(mock_charge_wallet_sync)
    profiler.add_function(mock_deduct_wallet_sync)
    profiler.run("mock_register_customer_sync()")
    profiler.run("mock_delete_customer_sync()")
    profiler.run("mock_update_customer_sync()")
    profiler.run("mock_get_all_customers_sync()")
    profiler.run("mock_get_customer_sync()")
    profiler.run("mock_charge_wallet_sync()")
    profiler.run("mock_deduct_wallet_sync()")
    profiler.print_stats()


# Memory Profiling for All Functions
@profile
async def memory_profile():
    await register_customer_profile()
    await delete_customer_profile()
    await update_customer_profile()
    await get_all_customers_profile()
    await get_customer_profile()
    await charge_wallet_profile()
    await deduct_wallet_profile()


# Main Execution
if __name__ == "__main__":
    print("Profiling with cProfile:")
    profile_cprofile(register_customer_profile)
    profile_cprofile(delete_customer_profile)
    profile_cprofile(update_customer_profile)
    profile_cprofile(get_all_customers_profile)
    profile_cprofile(get_customer_profile)
    profile_cprofile(charge_wallet_profile)
    profile_cprofile(deduct_wallet_profile)

    print("\nProfiling line-by-line:")
    line_profile()

    print("\nProfiling memory usage:")
    asyncio.run(memory_profile())
