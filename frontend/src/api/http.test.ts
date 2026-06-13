import type { AxiosAdapter, InternalAxiosRequestConfig } from "axios";
import { describe, expect, it } from "vitest";

import { apiClient } from "./http";

describe("apiClient", () => {
  it("does not serialize FormData requests as JSON", async () => {
    let capturedConfig: InternalAxiosRequestConfig | undefined;
    const adapter: AxiosAdapter = async (config) => {
      capturedConfig = config;
      return {
        data: {},
        status: 200,
        statusText: "OK",
        headers: {},
        config,
        request: {}
      };
    };
    const formData = new FormData();
    formData.append("file", new File(["image-bytes"], "photo.jpg", { type: "image/jpeg" }));

    await apiClient.post("/galleries/gallery-1/photos/upload", formData, { adapter });

    expect(capturedConfig?.data).toBe(formData);
    expect(capturedConfig?.headers.get("Content-Type")).not.toContain("application/json");
  });
});
