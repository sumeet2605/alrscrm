import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { ProductionDashboardPage } from "./ProductionDashboardPage";

vi.mock("../../api/editing", () => ({
  getEditingMetrics: vi.fn(async () => ({
    pending_jobs: 2,
    assigned_jobs: 1,
    in_progress_jobs: 3,
    ready_for_review: 4,
    ready_for_delivery: 5,
    overdue_jobs: 1,
    average_editing_tat: 2.5,
    average_review_tat: 1.5,
    jobs_by_editor: { "editor@example.com": 3 },
    jobs_by_priority: { NORMAL: 2, URGENT: 1 },
    jobs_by_service_type: { NEWBORN: 3 },
    photos_edited_this_month: 42
  }))
}));

describe("ProductionDashboardPage", () => {
  it("renders production metrics", async () => {
    renderWithProviders(<ProductionDashboardPage />);

    expect(await screen.findByText("Production Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Pending Jobs")).toBeInTheDocument();
    expect(screen.getByText("Ready For Delivery")).toBeInTheDocument();
    expect(screen.getByText("Photos Edited This Month")).toBeInTheDocument();
    expect(screen.getByText("editor@example.com")).toBeInTheDocument();
  });
});
