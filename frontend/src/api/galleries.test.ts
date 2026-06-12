import { describe, expect, it, vi } from "vitest";

import { uploadGalleryPhoto } from "./galleries";
import { apiClient } from "./http";

vi.mock("./http", () => ({
  apiClient: {
    post: vi.fn()
  }
}));

describe("gallery API", () => {
  it("uploads gallery photos with the backend multipart field name", async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        data: {
          id: "photo-1",
          gallery_id: "gallery-1",
          file_name: "photo.jpg",
          storage_path: "signed-url",
          thumbnail_path: "thumb-url",
          file_size: 11,
          image_width: 1200,
          image_height: 800,
          sort_order: 1,
          is_active: true,
          uploaded_at: "2026-06-12T00:00:00Z"
        }
      }
    });
    const file = new File(["image-bytes"], "photo.jpg", { type: "image/jpeg" });

    await uploadGalleryPhoto("gallery-1", file, { image_width: 1200, image_height: 800 });

    expect(apiClient.post).toHaveBeenCalledWith(
      "/galleries/gallery-1/photos/upload",
      expect.any(FormData)
    );
    const formData = vi.mocked(apiClient.post).mock.calls[0][1] as FormData;
    expect(formData.get("file")).toBe(file);
    expect(formData.get("photo")).toBeNull();
    expect(formData.get("image_width")).toBe("1200");
    expect(formData.get("image_height")).toBe("800");
  });
});
