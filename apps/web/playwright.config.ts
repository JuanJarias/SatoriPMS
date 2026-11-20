import { defineConfig } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..');
const venvPython = path.join(repoRoot, '.venv', 'bin', 'python');
const pythonCmd = fs.existsSync(venvPython) ? venvPython : 'python3';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 45_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  use: {
    baseURL: 'http://127.0.0.1:5174',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    acceptDownloads: true,
  },
  webServer: [
    {
      command: `"${pythonCmd}" "${path.join(repoRoot, 'scripts', 'run_e2e_api.py')}"`,
      cwd: repoRoot,
      url: 'http://127.0.0.1:8081/api/v1/health',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        E2E_API_PORT: '8081',
        CORS_ORIGINS: '["http://127.0.0.1:5174","http://localhost:5174"]',
      },
    },
    {
      command: 'npx vite --host 127.0.0.1 --port 5174 --strictPort',
      cwd: __dirname,
      url: 'http://127.0.0.1:5174',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: {
        VITE_PROXY_TARGET: 'http://127.0.0.1:8081',
        VITE_API_URL: '',
      },
    },
  ],
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});
