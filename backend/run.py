import os
import sys
import asyncio
import uvicorn

# On Windows, enforce ProactorEventLoopPolicy for Playwright subprocesses if needed
if sys.platform == "win32":
    try:
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

# Add root and backend to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for p in [root_dir, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
