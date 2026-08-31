import os
import sys

# Add root directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    import uvicorn
    from apps.api.backend.main import app
except ImportError:
    # If installed locally
    from backend.main import app
    import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    print(f"🚀 [WebTestAI Python Engine] Running on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
