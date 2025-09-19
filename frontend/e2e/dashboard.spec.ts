import { test, expect } from "@playwright/test";

const environmentPayload = [
  {
    id: 1,
    location: "demo",
    temperature: 22.1,
    humidity: 44.5,
    air_quality_index: 31,
    created_at: new Date().toISOString()
  }
];

const devicePayload = [
  {
    id: 1,
    device_id: "demo-device",
    name: "Demo Sensor",
    status: "online",
    meta: {},
    updated_at: new Date().toISOString()
  }
];

const alarmPayload: any[] = [];

test("dashboard renders core flows with realtime updates", async ({ page }) => {
  await page.route("**/api/environment", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(environmentPayload)
    });
  });
  await page.route("**/api/devices", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(devicePayload)
    });
  });
  await page.route("**/api/alarms", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(alarmPayload)
    });
  });

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "IoT Command Center" })).toBeVisible();
  await expect(page.getByText("Demo Sensor")).toBeVisible();
  await expect(page.getByText("No alarms")).toBeVisible();
  await expect(page.getByText("Connecting...")).toBeVisible();

  await page.evaluate(() => {
    window.__iotRealtimeTestHooks?.triggerOpen();
  });
  await expect(page.getByText("Realtime Connected")).toBeVisible();

  await page.evaluate(() => {
    window.__iotRealtimeTestHooks?.emit("device.update", {
      id: 2,
      device_id: "demo-device",
      name: "Demo Sensor",
      status: "maintenance",
      meta: { firmware: "2.0.0" },
      updated_at: new Date().toISOString()
    });
  });
  await expect(page.getByText("maintenance")).toBeVisible();

  const alarmEvent = {
    id: 3,
    code: "DEVICE_OFFLINE",
    message: "Sensor disconnected",
    severity: "warning",
    device_id: "demo-device",
    created_at: new Date().toISOString()
  };
  await page.evaluate((event) => {
    window.__iotRealtimeTestHooks?.emit("alarm.raise", event);
  }, alarmEvent);
  await expect(page.getByText("DEVICE_OFFLINE")).toBeVisible();

  await page.evaluate(() => {
    window.__iotRealtimeTestHooks?.triggerClose();
  });
  await expect(page.getByText("Connecting...")).toBeVisible();
});
