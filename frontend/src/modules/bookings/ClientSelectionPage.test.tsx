import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Route, Routes } from "react-router-dom";

import { renderWithProviders } from "../../test/render";
import { ClientSelectionPage } from "./ClientSelectionPage";

const mocks = vi.hoisted(() => ({
  addPublicGalleryFavorite: vi.fn()
}));

vi.mock("../../api/galleries", () => ({
  getPublicGallery: vi.fn(async () => ({
    id: "gallery-1",
    organization_id: "org-1",
    branch_id: "branch-1",
    booking_id: "booking-1",
    booking_item_id: "item-1",
    gallery_name: "Client Gallery",
    gallery_status: "SELECTION_OPEN",
    created_by_user_id: "user-1",
    created_at: "2026-06-10T00:00:00Z",
    updated_at: "2026-06-10T00:00:00Z",
    photo_count: 1,
    favorite_count: 0,
    photos: [
      {
        id: "photo-1",
        gallery_id: "gallery-1",
        file_name: "photo.jpg",
        storage_path: "photo.jpg",
        thumbnail_path: null,
        file_size: 1000,
        image_width: 1200,
        image_height: 800,
        sort_order: 1,
        is_active: true,
        uploaded_at: "2026-06-10T00:00:00Z"
      }
    ],
    favorites: []
  })),
  addPublicGalleryFavorite: mocks.addPublicGalleryFavorite
}));

describe("ClientSelectionPage", () => {
  it("allows a client to favorite a photo", async () => {
    const user = userEvent.setup();
    mocks.addPublicGalleryFavorite.mockResolvedValue({ id: "favorite-1" });
    renderWithProviders(
      <Routes>
        <Route path="/client/galleries/:galleryId" element={<ClientSelectionPage />} />
      </Routes>,
      ["/client/galleries/gallery-1"]
    );

    expect(await screen.findByText("Client Gallery")).toBeInTheDocument();
    await user.type(screen.getByPlaceholderText("Your name"), "Client Parent");
    await user.type(screen.getByPlaceholderText("Email"), "client@example.com");
    await user.click(screen.getByRole("button", { name: "Select photo" }));

    await waitFor(() =>
      expect(mocks.addPublicGalleryFavorite).toHaveBeenCalledWith("gallery-1", {
        gallery_photo_id: "photo-1",
        selected_by_name: "Client Parent",
        selected_by_email: "client@example.com"
      }, undefined)
    );
  });
});
