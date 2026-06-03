const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:8000",
    headless: true,
  },
  workers: 1,
  webServer: {
    command: "python server.py",
    port: 8000,
    reuseExistingServer: true,
    timeout: 30000,
  },
});
