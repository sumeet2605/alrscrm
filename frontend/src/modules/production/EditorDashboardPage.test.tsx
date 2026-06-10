import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { EditorDashboardPage } from "./EditorDashboardPage";

vi.mock("../../api/editing", () => ({
  getEditorDashboard: vi.fn(async () => ({
    assigned_jobs: 6,
    due_today: 2,
    overdue: 1,
    completed_this_week: 4,
    current_workload: 7
  }))
}));

describe("EditorDashboardPage", () => {
  it("renders editor workload metrics", async () => {
    renderWithProviders(<EditorDashboardPage />);

    expect(await screen.findByText("Editor Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Assigned Jobs")).toBeInTheDocument();
    expect(screen.getByText("Due Today")).toBeInTheDocument();
    expect(screen.getByText("Current Workload")).toBeInTheDocument();
  });
});
