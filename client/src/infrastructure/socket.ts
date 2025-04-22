// infrastructure/sockets/socket.ts

import { io, Socket } from "socket.io-client";

export class SocketClient {
  private socket: Socket | null = null;
  private readonly url: string;

  constructor(url: string) {
    this.url = url;
  }

  public connect(clientId: string): void {
    if (this.socket && this.socket.connected) return;

    console.log("CONNECTING TO SOCKET...");
    if (!this.socket) {
      this.socket = io(this.url, {
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        autoConnect: true,
      });
    }

    this.socket.on("connect", () => {
      console.log("[SocketClient] Connected:", this.socket?.id);
      this.socket?.emit("register_client", { client_id: clientId });
    });

    this.socket.on("disconnect", (reason: string) => {
      console.warn("[SocketClient] Disconnected:", reason);
    });

    this.socket.on("connect_error", (err: Error) => {
      console.error("[SocketClient] Connection error:", err);
    });

    this.socket.connect();
  }

  public on(event: string, callback: (...args: any[]) => void): void {
    this.socket?.on(event, callback);
  }

  public off(event: string): void {
    this.socket?.off(event);
  }

  public emit(event: string, data?: any): void {
    this.socket?.emit(event, data);
  }

  public disconnect(): void {
    this.socket?.disconnect();
    this.socket = null;
  }

  public isConnected(): boolean {
    return this.socket?.connected || false;
  }

  public getSocketId(): string | null {
    return this.socket?.id || null;
  }
}

export const socketClient = new SocketClient("http://localhost:8005");
