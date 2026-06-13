import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { DeliveryQueuePage } from "./DeliveryQueuePage";

vi.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: "user-1",
      roles: [{ id: "role-1", name: "Owner" }]
    }
  })
}));

vi.mock("../../api/delivery", () => ({
  approveDeliveryReopen: vi.fn(),
  generateDeliveryZip: vi.fn(),
  listDeliveryJobs: vi.fn(async () => ({
    items: [
      {
        id: "delivery-1",
        delivery_number: "DL-2026-000001",
        delivery_status: "PENDING",
        zip_generation_status: "PENDING",
        edited_photo_count: 12,
        download_count: 0,
        max_downloads: 10,
        expiry_date: "2026-09-10",
        gallery_name: "Newborn Finals",
        booking_number: "BK-001",
        family_name: "Sharma Family",
        service_type: "NEWBORN"
      }
    ],
    meta: { page: 1, page_size: 50, total: 1, pages: 1 }
  })),
  sendDelivery: vi.fn()
}));

describe("DeliveryQueuePage", () => {
  it("renders delivery jobs", async () => {
    renderWithProviders(<DeliveryQueuePage />);

    expect(await screen.findByText("DL-2026-000001")).toBeInTheDocument();
    expect(screen.getByText("Newborn Finals")).toBeInTheDocument();
    expect(screen.getByText("Sharma Family")).toBeInTheDocument();
    expect(screen.getByText("0/10")).toBeInTheDocument();
  });
});
