import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { UserManagementPage } from "./UserManagementPage";
import { renderWithProviders } from "../../test/render";

vi.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      organization_id: "org-1",
      branch_id: "branch-1"
    }
  })
}));

vi.mock("../../api/identity", () => ({
  listUsers: vi.fn().mockResolvedValue({
    items: [
      {
        id: "user-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        email: "admin@admin.com",
        first_name: "Admin",
        last_name: "User",
        is_active: true,
        roles: [{ id: "role-1", name: "Owner" }],
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z"
      }
    ],
    meta: { page: 1, page_size: 10, total: 1, pages: 1 }
  }),
  listRoles: vi.fn().mockResolvedValue([
    { id: "role-1", name: "Owner", permissions: [], is_platform: false, priority: 900 }
  ]),
  listBranches: vi.fn().mockResolvedValue({
    items: [{ id: "branch-1", name: "Main Branch" }],
    meta: { page: 1, page_size: 100, total: 1, pages: 1 }
  }),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deactivateUser: vi.fn()
}));

describe("UserManagementPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders user management data from the API layer", async () => {
    renderWithProviders(<UserManagementPage />, ["/users"]);

    expect(screen.getByRole("heading", { name: "Users" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /new user/i })).toBeInTheDocument();
    expect(await screen.findByText("admin@admin.com")).toBeInTheDocument();
  });
});
