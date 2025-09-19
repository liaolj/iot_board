export interface EnvironmentReading {
  id: number;
  location: string;
  temperature: number;
  humidity: number;
  air_quality_index: number;
  created_at: string;
}

export interface DeviceStatus {
  id: number;
  device_id: string;
  name: string;
  status: string;
  meta: Record<string, any>;
  updated_at: string;
}

export interface AlarmEvent {
  id: number;
  code: string;
  message: string;
  severity: "info" | "warning" | "critical";
  device_id?: string | null;
  created_at: string;
}

export interface RealtimeMessage<T = any> {
  event: string;
  payload: T;
  created_at: string;
}
