import { render, screen, waitFor } from "@testing-library/react";
import DashboardPage from "../Dashboard";
import type { AlarmEvent, DeviceStatus, EnvironmentReading } from "../../types/realtime";

const realtimeEvents: Record<string, ((payload: unknown) => void)[]> = {};
const openHandlers: Set<(event: Event) => void> = new Set();
const closeHandlers: Set<(event: CloseEvent) => void> = new Set();

vi.mock("../../services/realtime", () => ({
  default: {
    on: vi.fn((event: string, handler: (payload: unknown) => void) => {
      if (!realtimeEvents[event]) {
        realtimeEvents[event] = [];
      }
      realtimeEvents[event].push(handler);
      return () => {
        realtimeEvents[event] = realtimeEvents[event].filter((cb) => cb !== handler);
      };
    }),
    onOpen: vi.fn((handler: (event: Event) => void) => {
      openHandlers.add(handler);
      return () => openHandlers.delete(handler);
    }),
    onClose: vi.fn((handler: (event: CloseEvent) => void) => {
      closeHandlers.add(handler);
      return () => closeHandlers.delete(handler);
    }),
    onError: vi.fn((handler: (event: Event) => void) => {
      return () => {
        // no-op for tests
      };
    })
  }
}));

describe("DashboardPage", () => {
  const environment: EnvironmentReading[] = [
    {
      id: 1,
      location: "field",
      temperature: 25,
      humidity: 45,
      air_quality_index: 32,
      created_at: new Date().toISOString()
    }
  ];
  const devices: DeviceStatus[] = [
    {
      id: 1,
      device_id: "node-1",
      name: "Edge Node",
      status: "online",
      meta: {},
      updated_at: new Date().toISOString()
    }
  ];
  const alarms: AlarmEvent[] = [
    {
      id: 1,
      code: "DEVICE_OFFLINE",
      message: "Node lost connectivity",
      severity: "warning",
      device_id: "node-1",
      created_at: new Date().toISOString()
    }
  ];

  beforeEach(() => {
    Object.keys(realtimeEvents).forEach((key) => delete realtimeEvents[key]);
    openHandlers.clear();
    closeHandlers.clear();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo) => {
      if (typeof input === "string" && input.endsWith("/api/environment")) {
        return new Response(JSON.stringify(environment), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }
      if (typeof input === "string" && input.endsWith("/api/devices")) {
        return new Response(JSON.stringify(devices), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }
      if (typeof input === "string" && input.endsWith("/api/alarms")) {
        return new Response(JSON.stringify(alarms), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }
      throw new Error(`Unexpected fetch ${input}`);
    }));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads initial data and reacts to realtime connection events", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Edge Node")).toBeInTheDocument();
      expect(screen.getByText("DEVICE_OFFLINE")).toBeInTheDocument();
      expect(screen.queryByText("Realtime Connected")).not.toBeInTheDocument();
    });

    openHandlers.forEach((handler) => handler(new Event("open")));

    await waitFor(() => {
      expect(screen.getByText("Realtime Connected")).toBeInTheDocument();
    });

    const newAlarm: AlarmEvent = {
      id: 2,
      code: "TEMP_HIGH",
      message: "Temperature exceeded threshold",
      severity: "critical",
      device_id: "node-1",
      created_at: new Date().toISOString()
    };

    const listeners = realtimeEvents["alarm.raise"] ?? [];
    listeners.forEach((listener) => listener(newAlarm));

    await waitFor(() => {
      expect(screen.getByText("TEMP_HIGH")).toBeInTheDocument();
    });

    const closeEvent = typeof CloseEvent !== "undefined"
      ? new CloseEvent("close")
      : (new Event("close") as CloseEvent);
    closeHandlers.forEach((handler) => handler(closeEvent));

    await waitFor(() => {
      expect(screen.getByText("Connecting...")).toBeInTheDocument();
    });
  });
});
