import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Route, Routes } from "react-router-dom";

import { markEditingReadyForDelivery } from "../../api/editing";
import { renderWithProviders } from "../../test/render";
import { EditingJobDetailPage } from "./EditingJobDetailPage";

const editingJob = {
  id: "job-1",
  organization_id: "org-1",
  branch_id: "branch-1",
  booking_id: "booking-1",
  booking_item_id: "item-1",
  gallery_id: "gallery-1",
  assigned_editor_id: "editor-1",
  priority: "NORMAL",
  editing_status: "APPROVED",
  selected_photo_count: 12,
  completed_photo_count: 12,
  due_date: "2026-06-17",
  started_at: "2026-06-11T00:00:00Z",
  completed_at: "2026-06-12T00:00:00Z",
  notes: null,
  created_at: "2026-06-10T00:00:00Z",
  updated_at: "2026-06-12T00:00:00Z",
  assigned_editor: {
    id: "editor-1",
    first_name: "Esha",
    last_name: "Editor",
    email: "esha@example.com"
  },
  reviews: [],
  gallery_name: "Newborn Selection",
  booking_number: "BK-001",
  family_name: "Sharma Family",
  service_type: "NEWBORN"
};

vi.mock("../../api/identity", () => ({
  listUsers: vi.fn(async () => ({
    items: [
      {
        id: "editor-1",
        first_name: "Esha",
        last_name: "Editor",
        email: "esha@example.com",
        roles: [{ id: "role-editor", name: "Editor" }]
      }
    ],
    meta: { page: 1, page_size: 100, total: 1, pages: 1 }
  }))
}));

vi.mock("../../api/editing", () => ({
  getEditingJob: vi.fn(async () => editingJob),
  updateEditingJob: vi.fn(async () => editingJob),
  assignEditingJob: vi.fn(async () => editingJob),
  startEditingJob: vi.fn(async () => editingJob),
  submitEditingReview: vi.fn(async () => editingJob),
  approveEditingJob: vi.fn(async () => editingJob),
  rejectEditingJob: vi.fn(async () => editingJob),
  markEditingReadyForDelivery: vi.fn(async () => ({
    ...editingJob,
    editing_status: "READY_FOR_DELIVERY"
  }))
}));

describe("EditingJobDetailPage", () => {
  it("marks an approved editing job ready for delivery", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <Routes>
        <Route path="/production/editing/:jobId" element={<EditingJobDetailPage />} />
      </Routes>,
      ["/production/editing/job-1"]
    );

    expect(await screen.findByText("Newborn Selection")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Ready For Delivery" }));

    await waitFor(() => expect(markEditingReadyForDelivery).toHaveBeenCalledWith("job-1"));
  });
});
