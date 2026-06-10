import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { createPackage } from "../../api/bookings";
import { renderWithProviders } from "../../test/render";
import { PackageManagementPage } from "./PackageManagementPage";

vi.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: "user-1",
      organization_id: "org-1",
      branch_id: null,
      roles: [{ id: "role-1", name: "Owner" }]
    }
  })
}));

vi.mock("../../api/identity", () => ({
  listBranches: vi.fn().mockResolvedValue({
    items: [
      {
        id: "branch-1",
        organization_id: "org-1",
        name: "Main Branch",
        code: "MAIN",
        city: "Mumbai",
        is_active: true,
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z"
      }
    ],
    meta: { page: 1, page_size: 100, total: 1, pages: 1 }
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

  it("creates a package from the package management form", async () => {
    const user = userEvent.setup();
    renderWithProviders(<PackageManagementPage />, ["/packages"]);

    await user.click(screen.getByRole("button", { name: /New Package/i }));
    const dialog = await screen.findByRole("dialog", { name: "New Catalog Item" });
    expect(await within(dialog).findByText("Main Branch · Mumbai")).toBeInTheDocument();
    await user.type(within(dialog).getByLabelText("Name"), "Cake Smash Classic");
    await user.clear(within(dialog).getByLabelText("Price"));
    await user.type(within(dialog).getByLabelText("Price"), "15000");
    await user.click(within(dialog).getByRole("button", { name: "OK" }));

    await waitFor(() => {
      expect(createPackage).toHaveBeenCalledWith(
        expect.objectContaining({
          organization_id: "org-1",
          branch_id: "branch-1",
          name: "Cake Smash Classic",
          service_type: "NEWBORN",
          price: 15000
        })
      );
    });
  });
});
