/**
 * Request Manager - Handles request lifecycle and cancellation
 * Following Single Responsibility Principle (SRP)
 */

export class RequestManager {
  private activeRequests: Map<string, AbortController> = new Map();

  /**
   * Creates an AbortController for a request
   */
  createController(key: string): AbortController {
    // Cancel any existing request with the same key
    this.cancel(key);

    const controller = new AbortController();
    this.activeRequests.set(key, controller);

    return controller;
  }

  /**
   * Gets the AbortSignal for a request
   */
  getSignal(key: string): AbortSignal | undefined {
    return this.activeRequests.get(key)?.signal;
  }

  /**
   * Cancels a specific request
   */
  cancel(key: string): void {
    const controller = this.activeRequests.get(key);
    if (controller) {
      controller.abort();
      this.activeRequests.delete(key);
    }
  }

  /**
   * Cancels all active requests
   */
  cancelAll(): void {
    for (const controller of this.activeRequests.values()) {
      controller.abort();
    }
    this.activeRequests.clear();
  }

  /**
   * Removes a completed request from tracking
   */
  complete(key: string): void {
    this.activeRequests.delete(key);
  }

  /**
   * Gets the count of active requests
   */
  getActiveCount(): number {
    return this.activeRequests.size;
  }

  /**
   * Checks if a request is active
   */
  isActive(key: string): boolean {
    return this.activeRequests.has(key);
  }
}

// Singleton instance
export const requestManager = new RequestManager();