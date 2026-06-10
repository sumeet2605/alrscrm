import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { PackageManagementPage } from "./PackageManagementPage";

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
  listPackages: vi.fn().mockResolvedValue([
    {
      id: "package-1",
      organization_id: "org-1",
      branch_id: "branch-1",
      name: "Newborn Signature",
      service_type: "NEWBORN",
      description: null,
      price: "20000.00",
      is_active: true,
      created_at: "2026-06-10T00:00:00Z",
      updated_at: "2026-06-10T00:00:00Z"
    }
  ]),
  listAddons: vi.fn().mockResolvedValue([
    {
      id: "addon-1",
      organization_id: "org-1",
      branch_id: "branch-1",
      name: "Album",
      description: null,
      price: "5000.00",
      is_active: true,
      created_at: "2026-06-10T00:00:00Z",
      updated_at: "2026-06-10T00:00:00Z"
    }
  ]),
  createPackage: vi.fn(),
  updatePackage: vi.fn(),
  createAddon: vi.fn(),
  updateAddon: vi.fn()
}));

describe("PackageManagementPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders package and addon reference data", async () => {
    renderWithProviders(<PackageManagementPage />, ["/packages"]);

    expect(screen.getByRole("heading", { name: "Packages" })).toBeInTheDocument();
    expect(await screen.findByText("Newborn Signature")).toBeInTheDocument();
    expect(screen.getByText("Album")).toBeInTheDocument();
  });
});
