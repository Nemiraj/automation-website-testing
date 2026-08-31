// DEPRECATED: Node.js backend has been completely migrated to Python.
// Please use `apps/api/server.py` or `apps/api/backend/main.py`.
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const backendDir = path.resolve(__dirname, '..');

const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
console.log('🚀 Redirecting to Python FastAPI backend...');
spawn(pythonCmd, ['server.py'], { cwd: backendDir, stdio: 'inherit', shell: true });
