import { useEffect, useState } from "react";
import realtimeService from "../services/realtime";
import { AlarmEvent } from "../types/realtime";

interface Props {
  initialAlarms?: AlarmEvent[];
}

export default function AlarmPanel({ initialAlarms = [] }: Props) {
  const [alarms, setAlarms] = useState<AlarmEvent[]>(initialAlarms);

  useEffect(() => {
    setAlarms(initialAlarms);
  }, [initialAlarms]);

  useEffect(() => {
    const unsubscribe = realtimeService.on("alarm.raise", (payload) => {
      setAlarms((prev) => [payload as AlarmEvent, ...prev].slice(0, 20));
    });
    return () => unsubscribe();
  }, []);

  return (
    <section className="card">
      <header className="card__header">
        <h2>Alarms</h2>
      </header>
      <div className="card__body alarm-list">
        {alarms.length === 0 && <div>No alarms</div>}
        {alarms.map((alarm) => (
          <div key={alarm.id} className={`alarm alarm--${alarm.severity}`}>
            <div className="alarm__title">{alarm.code}</div>
            <div className="alarm__message">{alarm.message}</div>
            <div className="alarm__time">{new Date(alarm.created_at).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
