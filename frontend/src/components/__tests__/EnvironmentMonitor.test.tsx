import { render, screen, waitFor } from "@testing-library/react";
import EnvironmentMonitor from "../EnvironmentMonitor";
import type { EnvironmentReading } from "../../types/realtime";

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

describe("EnvironmentMonitor", () => {
  beforeEach(() => {
    Object.keys(eventCallbacks).forEach((key) => delete eventCallbacks[key]);
  });

  it("renders the latest reading and updates on realtime events", async () => {
    const initial: EnvironmentReading = {
      id: 1,
      location: "lab",
      temperature: 20.2,
      humidity: 40.5,
      air_quality_index: 35,
      created_at: new Date().toISOString()
    };

    render(<EnvironmentMonitor initialReadings={[initial]} />);

    expect(screen.getByText(/20\.2°C/)).toBeInTheDocument();
    expect(screen.getByText(/40\.5%/)).toBeInTheDocument();
    expect(screen.getByText(/35/)).toBeInTheDocument();

    const update: EnvironmentReading = {
      id: 2,
      location: "lab",
      temperature: 23.5,
      humidity: 50.1,
      air_quality_index: 30,
      created_at: new Date().toISOString()
    };

    const listeners = eventCallbacks["environment.update"] ?? [];
    listeners.forEach((listener) => listener(update));

    await waitFor(() => {
      expect(screen.getByText(/23\.5°C/)).toBeInTheDocument();
      expect(screen.getByText(/50\.1%/)).toBeInTheDocument();
      expect(screen.getByText(/30/)).toBeInTheDocument();
    });
  });
});
