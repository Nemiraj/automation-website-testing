import os
import sys
import uvicorn

# Add root directory and backend directory to python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

if __name__ == "__main__":
    print("=" * 60)
    print(" 🚀 Starting WebTest AI Python FastAPI Backend Engine (Port 4000)")
    print("=" * 60)
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=4000,
        reload=True
    )
