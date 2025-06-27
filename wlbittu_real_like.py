import aiohttp

async def login_guest(uid, password):
    # Simulated login to guest account
    return {"token": f"mock-token-for-{uid}"}

async def send_like(token, target_uid):
    # Simulated like sending
    return {"success": True}