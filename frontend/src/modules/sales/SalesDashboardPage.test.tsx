import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SalesDashboardPage } from "./SalesDashboardPage";
import { renderWithProviders } from "../../test/render";

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

vi.mock("../../api/sales", () => ({
  getPipeline: vi.fn().mockResolvedValue({
    NEW: [
      {
        id: "opportunity-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        family_id: "family-1",
        assigned_to_user_id: "user-1",
        opportunity_type: "NEWBORN",
        current_stage: "NEW",
        estimated_value: "20000.00",
        probability: 25,
        expected_booking_date: "2026-08-20",
        lost_reason_id: null,
        notes: null,
        deleted_at: null,
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z",
        family: {
          id: "family-1",
          family_code: "ALS-000001",
          primary_contact_name: "Aarav Sharma",
          primary_contact_phone: "+91 90000 00001"
        },
        assigned_to_user: null,
        lost_reason: null,
        followups: [],
        opportunity_notes: [],
        stage_history: []
      }
    ],
    PACKAGE_SENT: [],
    INTERESTED: [],
    NEED_FOLLOW_UP: [],
    THINKING: [],
    BOOKED: [],
    LOST: []
  }),
  getSalesMetrics: vi.fn().mockResolvedValue({
    open_opportunities: 1,
    booked_opportunities: 0,
    lost_opportunities: 0,
    conversion_rate: 0,
    pending_followups: 1,
    missed_followups: 0,
    follow_up_compliance: 100,
    average_opportunity_value: 20000
  }),
  listFollowUps: vi.fn().mockResolvedValue({
    items: [],
    meta: { page: 1, page_size: 5, total: 0, pages: 0 }
  }),
  listLostReasons: vi.fn().mockResolvedValue([]),
  updateOpportunity: vi.fn()
}));

describe("SalesDashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders pipeline opportunities and KPI labels from the API layer", async () => {
    renderWithProviders(<SalesDashboardPage />, ["/sales"]);

    expect(screen.getByRole("heading", { name: "Sales Pipeline" })).toBeInTheDocument();
    expect(screen.getByText("Follow Up Compliance")).toBeInTheDocument();
    expect(await screen.findByText("Aarav Sharma")).toBeInTheDocument();
    expect(screen.getByText(/ALS-000001/)).toBeInTheDocument();
  });
});
