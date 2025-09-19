import { render, screen, waitFor } from "@testing-library/react";
import DeviceStatusBoard from "../DeviceStatusBoard";
import type { DeviceStatus } from "../../types/realtime";

const eventCallbacks: Record<string, ((payload: unknown) => void)[]> = {};

vi.mock("../../services/realtime", () => {
  return {
    default: {
      on: vi.fn((event: string, handler: (payload: unknown) => void) => {
        if (!eventCallbacks[event]) {
          eventCallbacks[event] = [];
        }
        eventCallbacks[event].push(handler);
        return () => {
          eventCallbacks[event] = eventCallbacks[event].filter((cb) => cb !== handler);
        };
      })
    }
  };
});

describe("DeviceStatusBoard", () => {
  beforeEach(() => {
    Object.keys(eventCallbacks).forEach((key) => delete eventCallbacks[key]);
  });

  it("renders initial devices and reacts to realtime updates", async () => {
    const initial: DeviceStatus = {
      id: 1,
      device_id: "edge-1",
      name: "Gateway",
      status: "online",
      meta: {},
      updated_at: new Date().toISOString()
    };

    render(<DeviceStatusBoard initialDevices={[initial]} />);

    expect(screen.getByText("Gateway")).toBeInTheDocument();
    expect(screen.getByText("online")).toBeInTheDocument();

    const update: DeviceStatus = {
      ...initial,
      status: "offline"
    };

    const listeners = eventCallbacks["device.update"] ?? [];
    listeners.forEach((listener) => listener(update));

    await waitFor(() => {
      const status = screen.getByText("offline");
      expect(status).toBeInTheDocument();
      const container = status.closest(".device");
      expect(container).toHaveClass("status--danger");
    });
  });
});
