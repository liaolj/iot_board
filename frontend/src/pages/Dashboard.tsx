import { useEffect, useState } from "react";
import AlarmPanel from "../components/AlarmPanel";
import DeviceStatusBoard from "../components/DeviceStatusBoard";
import EnvironmentMonitor from "../components/EnvironmentMonitor";
import realtimeService from "../services/realtime";
import { AlarmEvent, DeviceStatus, EnvironmentReading } from "../types/realtime";

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}`);
  }
  return response.json();
}

export default function DashboardPage() {
  const [environment, setEnvironment] = useState<EnvironmentReading[]>([]);
  const [devices, setDevices] = useState<DeviceStatus[]>([]);
  const [alarms, setAlarms] = useState<AlarmEvent[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchJson<EnvironmentReading[]>("/api/environment"),
      fetchJson<DeviceStatus[]>("/api/devices"),
      fetchJson<AlarmEvent[]>("/api/alarms"),
    ])
      .then(([envData, deviceData, alarmData]) => {
        setEnvironment(envData);
        setDevices(deviceData);
        setAlarms(alarmData);
      })
      .catch((error) => console.error(error));
  }, []);

  useEffect(() => {
    const handleOpen = () => setConnected(true);
    const handleClose = () => setConnected(false);
    const offOpen = realtimeService.onOpen(handleOpen);
    const offClose = realtimeService.onClose(handleClose);
    const offError = realtimeService.onError(() => setConnected(false));
    return () => {
      offOpen();
      offClose();
      offError();
    };
  }, []);

  return (
    <main className="dashboard">
      <header className="dashboard__header">
        <h1>IoT Command Center</h1>
        <div className={`status-indicator ${connected ? "is-online" : "is-offline"}`}>
          {connected ? "Realtime Connected" : "Connecting..."}
        </div>
      </header>
      <div className="dashboard__grid">
        <EnvironmentMonitor initialReadings={environment} />
        <DeviceStatusBoard initialDevices={devices} />
        <AlarmPanel initialAlarms={alarms} />
      </div>
    </main>
  );
}
