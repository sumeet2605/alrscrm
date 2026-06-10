import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Route, Routes } from "react-router-dom";

import { updateGallery } from "../../api/galleries";
import { renderWithProviders } from "../../test/render";
import { GalleryDetailsPage } from "./GalleryDetailsPage";

const gallery = {
  id: "gallery-1",
  organization_id: "org-1",
  branch_id: "branch-1",
  booking_id: "booking-1",
  booking_item_id: "item-1",
  gallery_name: "Newborn Selection",
  gallery_status: "SELECTION_OPEN",
  created_by_user_id: "user-1",
  expires_at: null,
  created_at: "2026-06-10T00:00:00Z",
  updated_at: "2026-06-10T00:00:00Z",
  booking_number: "BK-001",
  family_name: "Sharma Family",
  photo_count: 1,
  favorite_count: 0,
  selection_limit: 20,
  selection_count: 0,
  selection_locked: false,
  selection_submitted_at: null,
  selection_deadline: null,
  allow_download: false,
  allow_watermark: true,
  reopen_count: 0,
  photos: [
    {
      id: "photo-1",
      gallery_id: "gallery-1",
      file_name: "photo.jpg",
      storage_path: "photo.jpg",
      thumbnail_path: null,
      file_size: 2048,
      image_width: 1600,
      image_height: 1200,
      sort_order: 1,
      is_active: true,
      uploaded_at: "2026-06-10T00:00:00Z"
    }
  ],
  favorites: []
};

vi.mock("../../api/galleries", () => ({
  getGallery: vi.fn(async () => gallery),
  updateGallery: vi.fn(async (_id: string, payload: object) => ({ ...gallery, ...payload })),
  reopenSelection: vi.fn(async () => gallery),
  createUpgradeRequest: vi.fn(async () => ({ id: "upgrade-1" }))
}));

describe("GalleryDetailsPage", () => {
  it("shares a gallery link and saves password settings", async () => {
    const user = userEvent.setup();

    renderWithProviders(
      <Routes>
        <Route path="/galleries/:galleryId" element={<GalleryDetailsPage />} />
      </Routes>,
      ["/galleries/gallery-1"]
    );

    expect(await screen.findByText("Newborn Selection")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Share gallery" }));
    const dialog = await screen.findByRole("dialog", { name: "Share Gallery" });

    expect(within(dialog).getByDisplayValue("http://localhost:3000/client/galleries/gallery-1")).toBeInTheDocument();

    await user.type(within(dialog).getByLabelText("Gallery Password"), "Client@123");
    await user.click(within(dialog).getByRole("button", { name: "Save Sharing Settings" }));

    await waitFor(() => {
      expect(updateGallery).toHaveBeenCalledWith(
        "gallery-1",
        expect.objectContaining({ password: "Client@123" })
      );
    });
  });
});
