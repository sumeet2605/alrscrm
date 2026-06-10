import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { BookingListPage } from "./BookingListPage";

vi.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: "user-1",
      organization_id: "org-1",
      branch_id: "branch-1",
      roles: [{ id: "role-1", name: "Owner" }]
    }
  })
}));

vi.mock("../../api/bookings", () => ({
  listBookings: vi.fn().mockResolvedValue({
    items: [
      {
        id: "booking-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        family_id: "family-1",
        opportunity_id: "opportunity-1",
        booking_number: "BK-BKG-2026-000001",
        booking_status: "CONFIRMED",
        total_amount: "24000.00",
        advance_received: "5000.00",
        balance_amount: "19000.00",
        booking_date: "2026-06-10",
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z",
        family: {
          id: "family-1",
          family_code: "ALS-000001",
          primary_contact_name: "Aarav Sharma",
          primary_contact_phone: "+91 90000 00001"
        },
        opportunity: null,
        items: []
      }
    ],
    meta: { page: 1, page_size: 10, total: 1, pages: 1 }
  }),
  deleteBooking: vi.fn()
}));

describe("BookingListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders booking rows from the API layer", async () => {
    renderWithProviders(<BookingListPage />, ["/bookings"]);

    expect(screen.getByRole("heading", { name: "Bookings" })).toBeInTheDocument();
    expect(await screen.findByText("BK-BKG-2026-000001")).toBeInTheDocument();
    expect(screen.getByText(/Aarav Sharma/)).toBeInTheDocument();
    expect(screen.getByText("₹24,000")).toBeInTheDocument();
  });
});
