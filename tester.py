import asyncio, time, statistics, httpx

CB_PRODUCT = "ETH-PERP-INTX"
CB_API_KEY = "organizations/953fdc21-164b-4d14-ae23-97d2d1a039d0/apiKeys/202cde83-1b19-4571-93b6-24f2e5c67908"
CB_API_SECRET = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIPJByatd23FWv6u5nIei4FMKV81frqRptsVp9ntiJ2b+oAoGCCqGSM49
AwEHoUQDQgAE7dw0bcTnben92UjGWJznFyBdBN7NDNFCKkbDbuWsqzViHptttaok
SHAdv/G8x9ew7qnhecGgsef1mObW63OALQ==
-----END EC PRIVATE KEY-----
"""


# Orderly
ORDERLY_SYMBOL = "PERP_ETH_USDC"
BASE_URL = "https://api.orderly.org"

ORDERLY_ACCOUNT_ID  = "0x64d6a5db107bf93cf8b840b3034d71e4c220d491db771018ed058a024ab99d94"
ORDERLY_PUBLIC_KEY  = "ed25519:BDnyhF5uMPGNQHQ1vLbrbKDQUp6iqgDwveShLDxRoK82"
ORDERLY_PRIVATE_KEY = "5wMWZY3QcKS5BCsZrTDjmr7HTTovWHC6Pyngdkbm4zsy"  # base58
ORDERLY_CHAIN_ID    = "421611"

# Test order size
TEST_SIZE = "0.00"
# ======================================================
# Globals (will be reassigned)
# ======================================================
CB_CLIENT = None
OD_CLIENT = None

# Coinbase test
CB_ENDPOINT = "https://api.exchange.coinbase.com/api/v3/brokerage/orders"
CB_HEADERS = {"Content-Type": "application/json"}
def build_cb_order():
    import uuid
    return f'{{"client_order_id":"{uuid.uuid4()}","product_id":"ETH-PERP-INTX","side":"BUY","order_configuration":{{"market_market_ioc":{{"base_size":"0.00"}}}}}}'

# Orderly test
OD_ENDPOINT = "https://api.orderly.org/v1/order"
def build_od_order():
    return b'{"symbol":"PERP_ETH_USDC","order_quantity":0.0,"side":"SELL","order_type":"MARKET"}'


# ======================================================
# Fresh client builder (IMPORTANT)
# ======================================================
def new_clients():
    global CB_CLIENT, OD_CLIENT
    CB_CLIENT = httpx.AsyncClient(http2=True, timeout=2.0)
    OD_CLIENT = httpx.AsyncClient(http2=True, timeout=2.0)


# ======================================================
# Request wrappers
# ======================================================
async def send_cb():
    body = build_cb_order()
    return await CB_CLIENT.post(CB_ENDPOINT, headers=CB_HEADERS, content=body)

async def send_od():
    body = build_od_order()
    return await OD_CLIENT.post(OD_ENDPOINT, content=body)


# ======================================================
# Benchmark helpers
# ======================================================
def summary(name, arr):
    print(f"\n===== {name} SUMMARY =====")
    print(f"avg {statistics.mean(arr):.2f} ms")
    print(f"min {min(arr):.2f} ms")
    print(f"max {max(arr):.2f} ms")
    print(f"std {statistics.pstdev(arr):.2f} ms")
    print("===========================")

async def bench(name, func, trials=100):
    times = []
    for i in range(trials):
        t0 = time.perf_counter()
        await func()
        dt = (time.perf_counter() - t0) * 1000
        times.append(dt)
        print(f"[{name} {i+1:02d}] {dt:.2f} ms")
        await asyncio.sleep(0.01)
    summary(name, times)


# ======================================================
# Master runner
# ======================================================
async def run_benchmarks():
    global CB_CLIENT, OD_CLIENT

    # DESTROY old clients first
    try:
        await CB_CLIENT.aclose()
    except: pass
    try:
        await OD_CLIENT.aclose()
    except: pass

    CB_CLIENT = None
    OD_CLIENT = None

    # Build fresh connections
    new_clients()

    print("[WARM] Priming TLS…")
    await send_cb()
    await send_od()
    print("[WARM] Ready.\n")

    await bench("CB", send_cb)
    await bench("OD", send_od)

    # Keep open if you plan multiple runs:
    # await CB_CLIENT.aclose()
    # await OD_CLIENT.aclose()


# ======================================================
# Run inside notebook
# ======================================================
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_benchmarks())
