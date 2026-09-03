/**
 * CORTANA — Centralized API HTTP Client.
 * Handles environment base URLs, timeout configuration, headers, JSON serialization,
 * and structured error handling. Supports explicit mock-mode fallback when configured.
 */

export class ApiError extends Error {
  status: number;
  data?: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

// Safely obtain environment variables across Vite and Node test environments
const getEnvVar = (key: string, defaultValue: string): string => {
  try {
    if (typeof import.meta !== "undefined" && import.meta.env && import.meta.env[key] !== undefined) {
      return String(import.meta.env[key]);
    }
  } catch {
    // Ignore in non-meta environments
  }
  const proc = (globalThis as Record<string, unknown>).process as { env?: Record<string, string> } | undefined;
  if (proc && proc.env && proc.env[key] !== undefined) {
    return String(proc.env[key]);
  }
  return defaultValue;
};

export const API_BASE_URL: string = getEnvVar("VITE_API_BASE_URL", "http://localhost:8000");

export function isMockMode(): boolean {
  return getEnvVar("VITE_USE_MOCK_DATA", "false") === "true";
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 10000, ...fetchOptions } = options;
  
  // Normalize URL path
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${API_BASE_URL}${normalizedPath}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(fetchOptions.headers || {}),
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorBody: unknown;
      try {
        errorBody = await response.json();
      } catch {
        errorBody = await response.text();
      }
      
      const errorMsg =
        typeof errorBody === "object" && errorBody !== null && "error" in errorBody
          ? String((errorBody as { error: unknown }).error)
          : `HTTP ${response.status}: ${response.statusText}`;
          
      throw new ApiError(errorMsg, response.status, errorBody);
    }

    // Parse JSON
    return (await response.json()) as T;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) {
      throw err;
    }
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError(`Request timeout after ${timeoutMs}ms`, 408);
    }
    const message = err instanceof Error ? err.message : "Network request failed";
    throw new ApiError(message, 0, err);
  }
}
