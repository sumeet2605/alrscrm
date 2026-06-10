import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { GalleryManagementPage } from "./GalleryManagementPage";

vi.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: "user-1",
      organization_id: "org-1",
      branch_id: "branch-1",
      first_name: "Owner",
      last_name: "User",
      email: "owner@example.com",
      roles: [{ id: "role-1", name: "Owner" }]
    }
  })
}));

const mocks = vi.hoisted(() => ({
  createGallery: vi.fn()
}));

vi.mock("../../api/galleries", () => ({
  listGalleries: vi.fn(async () => ({
    items: [
      {
        id: "gallery-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        booking_id: "booking-1",
        booking_item_id: "item-1",
        gallery_name: "Newborn Selection",
        gallery_status: "SELECTION_OPEN",
        created_by_user_id: "user-1",
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z",
        booking_number: "BK-001",
        family_name: "Sharma Family",
        photo_count: 25,
        favorite_count: 12
      }
    ],
    meta: { page: 1, page_size: 50, total: 1, total_pages: 1 }
  })),
  getGalleryMetrics: vi.fn(async () => ({
    total_galleries: 1,
    photos_uploaded: 25,
    selection_open_galleries: 1,
    selection_closed_galleries: 0,
    favorite_count: 12
  })),
  createGallery: mocks.createGallery
}));

vi.mock("../../api/bookings", () => ({
  listBookings: vi.fn(async () => ({
    items: [
      {
        id: "booking-1",
        booking_number: "BK-001",
        family: { primary_contact_name: "Sharma Family" },
        items: [{ id: "item-1", service_type: "NEWBORN" }]
      }
    ],
    meta: { page: 1, page_size: 100, total: 1, total_pages: 1 }
  }))
}));

describe("GalleryManagementPage", () => {
  it("renders galleries and creates a gallery from a booking item", async () => {
    const user = userEvent.setup();
    mocks.createGallery.mockResolvedValue({ id: "gallery-2" });
    renderWithProviders(<GalleryManagementPage />);

    expect(await screen.findByText("Newborn Selection")).toBeInTheDocument();
    expect(screen.getByText("BK-001")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /new gallery/i }));
    await user.click(screen.getByRole("combobox", { name: /booking item/i }));
    await user.click(await screen.findByText("BK-001 · Sharma Family · Newborn"));
    await user.type(screen.getByLabelText(/gallery name/i), "Client Proofs");
    await user.click(screen.getByRole("button", { name: "OK" }));

    await waitFor(() =>
      expect(mocks.createGallery).toHaveBeenCalledWith(
        expect.objectContaining({
          booking_id: "booking-1",
          booking_item_id: "item-1",
          gallery_name: "Client Proofs"
        })
      )
    );
  });
});
