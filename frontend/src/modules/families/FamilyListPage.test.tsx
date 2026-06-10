import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { FamilyListPage } from "./FamilyListPage";
import { renderWithProviders } from "../../test/render";

vi.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      organization_id: "org-1",
      branch_id: "branch-1",
      roles: [{ id: "role-1", name: "Owner" }]
    }
  })
}));

vi.mock("../../api/families", () => ({
  listFamilies: vi.fn().mockResolvedValue({
    items: [
      {
        id: "family-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        family_code: "ALS-000001",
        primary_contact_name: "Aarav Sharma",
        primary_contact_phone: "+91 90000 00001",
        primary_contact_email: "aarav@example.com",
        partner_name: "Mira Sharma",
        partner_phone: null,
        partner_email: null,
        city: "Mumbai",
        expected_delivery_date: "2026-08-15",
        source: "INSTAGRAM",
        notes: null,
        status: "INTERESTED",
        deleted_at: null,
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z",
        members: [],
        address: null,
        service_interests: []
      }
    ],
    meta: { page: 1, page_size: 10, total: 1, pages: 1 }
  }),
  deleteFamily: vi.fn()
}));

vi.mock("../../api/identity", () => ({
  listBranches: vi.fn().mockResolvedValue({
    items: [{ id: "branch-1", name: "Main Branch" }],
    meta: { page: 1, page_size: 100, total: 1, pages: 1 }
  })
}));

describe("FamilyListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders family rows from the API layer", async () => {
    renderWithProviders(<FamilyListPage />, ["/families"]);

    expect(screen.getByRole("heading", { name: "Families" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /new family/i })).toBeInTheDocument();
    expect(await screen.findByText("ALS-000001")).toBeInTheDocument();
    expect(screen.getByText("Aarav Sharma")).toBeInTheDocument();
  });
});
