import { spawn, execSync } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

console.log('====================================================');
console.log('🚀 Initializing WebTest AI Platform...');
console.log('====================================================');

// Free port helper for Windows / Unix
function freePort(port) {
  try {
    if (process.platform === 'win32') {
      const output = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] });
      const lines = output.trim().split('\n');
      const pids = new Set();
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 5 && (parts[1].endsWith(`:${port}`) || parts[2]?.endsWith(`:${port}`))) {
          const pid = parts[parts.length - 1];
          if (pid && pid !== '0' && pid !== String(process.pid)) {
            pids.add(pid);
          }
        }
      }
      for (const pid of pids) {
        try {
          execSync(`taskkill /F /PID ${pid}`, { stdio: 'ignore' });
          console.log(`🧹 Freed occupied port ${port} (terminated PID ${pid})`);
        } catch (e) {}
      }
    } else {
      execSync(`npx kill-port ${port}`, { stdio: 'ignore' });
    }
  } catch (e) {
    // Port is free
  }
}

// Clean up ports 3000, 3001, 4000 if occupied
freePort(3000);
freePort(3001);
freePort(4000);

console.log('✨ Starting services: Frontend (3000), Backend (4000), Demo Target (3001)...');

function startProcess(name, command, args, cwd) {
  const proc = spawn(command, args, {
    cwd,
    shell: true,
    stdio: 'inherit',
    env: { ...process.env, FORCE_COLOR: '1' }
  });

  proc.on('error', (err) => {
    console.error(`[${name}] Error:`, err);
  });

  proc.on('exit', (code) => {
    if (code !== 0 && code !== null) {
      console.log(`[${name}] Process exited with code ${code}`);
    }
  });

  return proc;
}

// 1. Start Demo Sandbox Target (Port 3001)
const demoTarget = startProcess(
  'DemoTarget',
  'node',
  ['server.js'],
  path.join(rootDir, 'demo-target')
);

// 2. Start Python Backend API & Engine (Port 4000)
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
const apiServer = startProcess(
  'Python-Backend',
  pythonCmd,
  ['run_backend.py'],
  rootDir
);

// 3. Start Frontend React Web UI (Port 3000)
const webApp = startProcess(
  'Frontend-UI',
  'npx',
  ['vite', '--port', '3000'],
  path.join(rootDir, 'frontend')
);

process.on('SIGINT', () => {
  console.log('\n🛑 Stopping all WebTest AI services...');
  demoTarget.kill();
  apiServer.kill();
  webApp.kill();
  process.exit(0);
});
