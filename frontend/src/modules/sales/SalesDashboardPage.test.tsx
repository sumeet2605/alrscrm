import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { SalesDashboardPage } from "./SalesDashboardPage";
import { renderWithProviders } from "../../test/render";
import { updateOpportunity } from "../../api/sales";

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
  listLostReasons: vi.fn().mockResolvedValue([
    {
      id: "reason-1",
      name: "Stopped Responding",
      description: null,
      is_active: true,
      created_at: "2026-06-10T00:00:00Z",
      updated_at: "2026-06-10T00:00:00Z"
    }
  ]),
  updateOpportunity: vi.fn().mockResolvedValue({})
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

  it("requires a lost reason before moving an opportunity to lost", async () => {
    const user = userEvent.setup();
    const { container } = renderWithProviders(<SalesDashboardPage />, ["/sales"]);

    const card = await screen.findByText("Aarav Sharma");
    const lostColumn = container.querySelectorAll(".pipeline-column")[6];
    const dataTransfer = {
      data: new Map<string, string>(),
      setData(format: string, value: string) {
        this.data.set(format, value);
      },
      getData(format: string) {
        return this.data.get(format) ?? "";
      }
    };

    fireEvent.dragStart(card.closest(".pipeline-card")!, { dataTransfer });
    fireEvent.drop(lostColumn, { dataTransfer });

    const dialog = await screen.findByRole("dialog", { name: "Mark Opportunity Lost" });
    expect(within(dialog).getByText("Lost Reason")).toBeInTheDocument();

    await user.click(within(dialog).getByRole("combobox"));
    await user.click(await screen.findByText("Stopped Responding"));
    await user.type(within(dialog).getByLabelText("Notes"), "No response after package");
    await user.click(within(dialog).getByRole("button", { name: "OK" }));

    await waitFor(() => {
      expect(updateOpportunity).toHaveBeenCalledWith("opportunity-1", {
        current_stage: "LOST",
        lost_reason_id: "reason-1",
        stage_change_notes: "No response after package"
      });
    });
  });
});
