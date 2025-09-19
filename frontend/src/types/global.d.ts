declare global {
  interface Window {
    __iotRealtimeTestHooks?: {
      emit(event: string, payload: any): void;
      triggerOpen(): void;
      triggerClose(): void;
      triggerError(): void;
    };
  }
}

export {};
