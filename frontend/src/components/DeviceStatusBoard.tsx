import { useEffect, useState } from "react";
import realtimeService from "../services/realtime";
import { DeviceStatus } from "../types/realtime";

interface Props {
  initialDevices?: DeviceStatus[];
}

function statusColor(status: string) {
  switch (status) {
    case "online":
      return "status--success";
    case "offline":
      return "status--danger";
    case "maintenance":
      return "status--warning";
    default:
      return "status--info";
  }
}

export default function DeviceStatusBoard({ initialDevices = [] }: Props) {
  const [devices, setDevices] = useState<Record<string, DeviceStatus>>(() => {
    const map: Record<string, DeviceStatus> = {};
    initialDevices.forEach((device) => {
      map[device.device_id] = device;
    });
    return map;
  });

  const deviceList = Object.values(devices);

  useEffect(() => {
    const map: Record<string, DeviceStatus> = {};
    initialDevices.forEach((device) => {
      map[device.device_id] = device;
    });
    setDevices(map);
  }, [initialDevices]);

  useEffect(() => {
    const unsubscribe = realtimeService.on("device.update", (payload) => {
      const device = payload as DeviceStatus;
      setDevices((prev) => ({
        ...prev,
        [device.device_id]: device,
      }));
    });
    return () => unsubscribe();
  }, []);

  return (
    <section className="card">
      <header className="card__header">
        <h2>Devices</h2>
      </header>
      <div className="card__body device-list">
        {deviceList.length === 0 && <div>No devices yet</div>}
        {deviceList.map((device) => (
          <div key={device.device_id} className={`device ${statusColor(device.status)}`}>
            <div className="device__name">{device.name}</div>
            <div className="device__status">{device.status}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
