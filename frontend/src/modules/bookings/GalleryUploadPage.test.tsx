import { Route, Routes } from "react-router-dom";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { GalleryUploadPage } from "./GalleryUploadPage";

const mocks = vi.hoisted(() => ({
  uploadGalleryPhoto: vi.fn()
}));

vi.mock("../../api/galleries", () => ({
  getGallery: vi.fn(async () => ({
    id: "gallery-1",
    gallery_name: "UAT Gallery",
    photos: []
  })),
  uploadGalleryPhoto: mocks.uploadGalleryPhoto,
  deleteGalleryPhoto: vi.fn()
}));

class TestImage {
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  naturalWidth = 1200;
  naturalHeight = 800;

  set src(_value: string) {
    setTimeout(() => this.onload?.(), 0);
  }
}

function renderUploadPage() {
  return renderWithProviders(
    <Routes>
      <Route path="/galleries/:galleryId/upload" element={<GalleryUploadPage />} />
    </Routes>,
    ["/galleries/gallery-1/upload"]
  );
}

describe("GalleryUploadPage", () => {
  beforeEach(() => {
    mocks.uploadGalleryPhoto.mockReset();
    vi.stubGlobal("Image", TestImage);
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:photo")
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn()
    });
  });

  it("uploads multiple selected photos with five-way concurrency and per-file progress", async () => {
    const user = userEvent.setup();
    let activeUploads = 0;
    let maxActiveUploads = 0;
    mocks.uploadGalleryPhoto.mockImplementation(async (_galleryId, _file, _dimensions, options) => {
      activeUploads += 1;
      maxActiveUploads = Math.max(maxActiveUploads, activeUploads);
      options?.onUploadProgress?.({ loaded: 50, total: 100 });
      await new Promise((resolve) => setTimeout(resolve, 20));
      activeUploads -= 1;
      return { id: `photo-${mocks.uploadGalleryPhoto.mock.calls.length}` };
    });

    const { container } = renderUploadPage();
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const files = Array.from(
      { length: 10 },
      (_, index) => new File(["image-bytes"], `photo-${index + 1}.jpg`, { type: "image/jpeg" })
    );

    await user.upload(input, files);

    await waitFor(() => expect(mocks.uploadGalleryPhoto).toHaveBeenCalledTimes(10));
    await waitFor(() => expect(screen.getByText("Upload progress: 10 / 10")).toBeInTheDocument());
    expect(maxActiveUploads).toBeLessThanOrEqual(5);
    expect(mocks.uploadGalleryPhoto).toHaveBeenCalledWith(
      "gallery-1",
      expect.any(File),
      { image_width: 1200, image_height: 800 },
      expect.objectContaining({ onUploadProgress: expect.any(Function) })
    );
  });

  it("retries failed uploads and continues the remaining queue", async () => {
    const user = userEvent.setup();
    let activeUploads = 0;
    let maxActiveUploads = 0;
    const attemptsByFile = new Map<string, number>();
    mocks.uploadGalleryPhoto.mockImplementation(async (_galleryId, file: File) => {
      activeUploads += 1;
      maxActiveUploads = Math.max(maxActiveUploads, activeUploads);
      await new Promise((resolve) => setTimeout(resolve, 10));
      activeUploads -= 1;
      const attempts = (attemptsByFile.get(file.name) ?? 0) + 1;
      attemptsByFile.set(file.name, attempts);
      if (file.name === "photo-3.jpg") {
        throw new Error("Spaces upload failed");
      }
      return { id: `photo-${file.name}` };
    });

    const { container } = renderUploadPage();
    const input = container.querySelector('input[type="file"]') as HTMLInputElement;
    const files = Array.from(
      { length: 6 },
      (_, index) => new File(["image-bytes"], `photo-${index + 1}.jpg`, { type: "image/jpeg" })
    );

    await user.upload(input, files);

    await waitFor(() => expect(mocks.uploadGalleryPhoto).toHaveBeenCalledTimes(8));
    await waitFor(() => expect(screen.getByText("Upload progress: 5 / 6")).toBeInTheDocument());
    expect(attemptsByFile.get("photo-3.jpg")).toBe(3);
    expect(attemptsByFile.get("photo-6.jpg")).toBe(1);
    expect(maxActiveUploads).toBeLessThanOrEqual(5);
    expect(screen.getByText("Spaces upload failed")).toBeInTheDocument();
  });
});
