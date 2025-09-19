import mitt, { Emitter, Handler } from "mitt";

type RealtimeEvents = {
  message: any;
  open: Event;
  close: CloseEvent;
  error: Event;
};

type Listener = (payload: any) => void;

type EventMap = Record<string, Set<Listener>>;

const DEFAULT_ENDPOINT = "/api/ws";
const RECONNECT_INTERVAL = 3000;

export class RealtimeService {
  private socket: WebSocket | null = null;
  private emitter: Emitter<RealtimeEvents> = mitt<RealtimeEvents>();
  private eventMap: EventMap = {};
  private url: string;
  private reconnectTimer: number | null = null;
  private manualClose = false;
  private eventSource: EventSource | null = null;
  private failureCount = 0;
  private useSse = false;

  constructor(endpoint: string = DEFAULT_ENDPOINT) {
    this.url = this.resolveUrl(endpoint);
    this.connect();
    this.registerTestHooks();
  }

  private resolveUrl(endpoint: string): string {
    if (endpoint.startsWith("ws")) {
      return endpoint;
    }
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;
    return `${protocol}://${host}${endpoint}`;
  }

  private connect() {
    this.manualClose = false;
    if (this.useSse) {
      this.openSse();
      return;
    }
    this.socket = new WebSocket(this.url);
    this.socket.onopen = (event) => {
      if (this.reconnectTimer) {
        window.clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
      this.failureCount = 0;
      this.emitter.emit("open", event);
    };
    this.socket.onclose = (event) => {
      this.emitter.emit("close", event);
      this.socket = null;
      if (!this.manualClose) {
        this.scheduleReconnect();
      }
    };
    this.socket.onerror = (event) => {
      this.emitter.emit("error", event);
      this.failureCount += 1;
    };
    this.socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        this.emitter.emit("message", payload);
        this.dispatchEvent(payload.event, payload.payload);
      } catch (error) {
        console.error("Failed to parse realtime message", error);
      }
    };
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) {
      return;
    }
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null;
      if (this.failureCount >= 3) {
        this.useSse = true;
      }
      this.connect();
    }, RECONNECT_INTERVAL);
  }

  private openSse() {
    if (this.eventSource) {
      return;
    }
    const parsed = new URL(this.url);
    parsed.protocol = parsed.protocol === "wss:" ? "https:" : "http:";
    parsed.pathname = parsed.pathname.replace(/\/?ws$/, "/events");
    const sseUrl = parsed.toString();
    this.eventSource = new EventSource(sseUrl);
    this.eventSource.onopen = (event) => {
      this.failureCount = 0;
      this.emitter.emit("open", event as unknown as Event);
    };
    this.eventSource.onerror = (event) => {
      this.failureCount += 1;
      this.emitter.emit("error", event as unknown as Event);
      const closeEvent = new CloseEvent("close", {
        wasClean: false,
        code: 1006,
        reason: "SSE connection error",
      });
      this.emitter.emit("close", closeEvent);
      if (!this.manualClose) {
        this.eventSource?.close();
        this.eventSource = null;
        this.scheduleReconnect();
      }
    };
    this.eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        this.dispatchEvent(payload.event, payload.payload);
        this.emitter.emit("message", payload);
      } catch (error) {
        console.error("Failed to parse SSE message", error);
      }
    };
  }

  private dispatchEvent(event: string, payload: any) {
    const listeners = this.eventMap[event];
    if (!listeners) return;
    listeners.forEach((listener) => listener(payload));
  }

  onMessage(handler: Handler<RealtimeEvents["message"]>) {
    this.emitter.on("message", handler);
    return () => this.emitter.off("message", handler);
  }

  onOpen(handler: Handler<RealtimeEvents["open"]>) {
    this.emitter.on("open", handler);
    return () => this.emitter.off("open", handler);
  }

  onClose(handler: Handler<RealtimeEvents["close"]>) {
    this.emitter.on("close", handler);
    return () => this.emitter.off("close", handler);
  }

  onError(handler: Handler<RealtimeEvents["error"]>) {
    this.emitter.on("error", handler);
    return () => this.emitter.off("error", handler);
  }

  on(event: string, handler: Listener) {
    if (!this.eventMap[event]) {
      this.eventMap[event] = new Set();
    }
    this.eventMap[event].add(handler);
    return () => this.off(event, handler);
  }

  off(event: string, handler: Listener) {
    const listeners = this.eventMap[event];
    if (!listeners) return;
    listeners.delete(handler);
    if (listeners.size === 0) {
      delete this.eventMap[event];
    }
  }

  reconnect() {
    this.manualClose = false;
    if (this.socket || this.eventSource) {
      return;
    }
    this.connect();
  }

  close() {
    this.manualClose = true;
    this.failureCount = 0;
    this.useSse = false;
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private registerTestHooks() {
    if (typeof window === "undefined") {
      return;
    }
    const hooks = {
      emit: (event: string, payload: any) => {
        this.dispatchEvent(event, payload);
      },
      triggerOpen: () => {
        this.emitter.emit("open", new Event("open"));
      },
      triggerClose: () => {
        const closeEvent = typeof CloseEvent !== "undefined"
          ? new CloseEvent("close", { wasClean: true, code: 1000, reason: "test" })
          : (new Event("close") as unknown as CloseEvent);
        this.emitter.emit("close", closeEvent);
      },
      triggerError: () => {
        this.emitter.emit("error", new Event("error"));
      }
    };
    (window as any).__iotRealtimeTestHooks = hooks;
  }
}

const realtimeService = new RealtimeService();
export default realtimeService;
