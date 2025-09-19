import { useEffect, useState } from "react";
import realtimeService from "../services/realtime";
import { EnvironmentReading } from "../types/realtime";

interface Props {
  initialReadings?: EnvironmentReading[];
}

export default function EnvironmentMonitor({ initialReadings = [] }: Props) {
  const [readings, setReadings] = useState<EnvironmentReading[]>(initialReadings);

  useEffect(() => {
    setReadings(initialReadings);
  }, [initialReadings]);

  useEffect(() => {
    const unsubscribe = realtimeService.on("environment.update", (payload) => {
      setReadings((prev) => {
        const next = [payload as EnvironmentReading, ...prev];
        return next.slice(0, 10);
      });
    });
    return () => unsubscribe();
  }, []);

  const latest = readings[0];

  return (
    <section className="card">
      <header className="card__header">
        <h2>Environment</h2>
      </header>
      {latest ? (
        <div className="card__body">
          <div className="metric">
            <span className="metric__label">Temperature</span>
            <span className="metric__value">{latest.temperature.toFixed(1)}°C</span>
          </div>
          <div className="metric">
            <span className="metric__label">Humidity</span>
            <span className="metric__value">{latest.humidity.toFixed(1)}%</span>
          </div>
          <div className="metric">
            <span className="metric__label">AQI</span>
            <span className="metric__value">{latest.air_quality_index.toFixed(0)}</span>
          </div>
        </div>
      ) : (
        <div className="card__body">No data yet</div>
      )}
    </section>
  );
}
