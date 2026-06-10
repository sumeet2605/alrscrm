import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { updateOpportunity } from "../../api/sales";
import { renderWithProviders } from "../../test/render";
import { OpportunityDetailsPage } from "./OpportunityDetailsPage";

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

vi.mock("../../api/identity", () => ({
  listUsers: vi.fn().mockResolvedValue({
    items: [{ id: "user-1", first_name: "Owner", last_name: "User", email: "owner@example.com" }],
    meta: { page: 1, page_size: 100, total: 1, pages: 1 }
  })
}));

vi.mock("../../api/sales", () => ({
  getOpportunity: vi.fn().mockResolvedValue({
    id: "opportunity-1",
    organization_id: "org-1",
    branch_id: "branch-1",
    family_id: "family-1",
    assigned_to_user_id: "user-1",
    opportunity_type: "NEWBORN",
    current_stage: "PACKAGE_SENT",
    estimated_value: "20000.00",
    probability: 35,
    expected_booking_date: "2026-08-20",
    lost_reason_id: null,
    notes: "Package shared",
    deleted_at: null,
    created_at: "2026-06-10T00:00:00Z",
    updated_at: "2026-06-10T00:00:00Z",
    family: {
      id: "family-1",
      family_code: "ALS-000001",
      primary_contact_name: "Aarav Sharma",
      primary_contact_phone: "+91 90000 00001",
      primary_contact_email: "aarav@example.com",
      city: "Mumbai"
    },
    assigned_to_user: { id: "user-1", first_name: "Owner", last_name: "User", email: "owner@example.com" },
    lost_reason: null,
    followups: [],
    opportunity_notes: [],
    stage_history: []
  }),
  listLostReasons: vi.fn().mockResolvedValue([]),
  createFollowUp: vi.fn(),
  createOpportunityNote: vi.fn(),
  updateFollowUp: vi.fn(),
  updateOpportunity: vi.fn().mockResolvedValue({})
}));

describe("OpportunityDetailsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("saves the opportunity edit workflow from the edit route", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <Routes>
        <Route path="/sales/opportunities/:opportunityId" element={<OpportunityDetailsPage />} />
      </Routes>,
      ["/sales/opportunities/opportunity-1?edit=1"]
    );

    expect(await screen.findByText("Edit Opportunity")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Save Changes/i }));

    await waitFor(() => {
      expect(updateOpportunity).toHaveBeenCalledWith(
        "opportunity-1",
        expect.objectContaining({
          current_stage: "PACKAGE_SENT",
          opportunity_type: "NEWBORN",
          probability: 35,
          expected_booking_date: "2026-08-20"
        })
      );
    });
  });
});
