import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { EditingQueuePage } from "./EditingQueuePage";

vi.mock("../../api/editing", () => ({
  listEditingJobs: vi.fn(async () => ({
    items: [
      {
        id: "job-1",
        gallery_name: "Newborn Selection",
        booking_number: "BK-001",
        family_name: "Sharma Family",
        service_type: "NEWBORN",
        priority: "NORMAL",
        editing_status: "PENDING",
        selected_photo_count: 12,
        completed_photo_count: 0,
        due_date: "2026-06-17",
        reviews: []
      }
    ],
    meta: { page: 1, page_size: 50, total: 1, pages: 1 }
  }))
}));

describe("EditingQueuePage", () => {
  it("renders editing jobs", async () => {
    renderWithProviders(<EditingQueuePage />);

    expect(await screen.findByText("Newborn Selection")).toBeInTheDocument();
    expect(screen.getByText("BK-001")).toBeInTheDocument();
    expect(screen.getByText("Sharma Family")).toBeInTheDocument();
    expect(screen.getByText("0/12")).toBeInTheDocument();
  });
});
