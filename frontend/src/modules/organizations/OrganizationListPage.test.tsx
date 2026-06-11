import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { OrganizationListPage } from "./OrganizationListPage";
import { renderWithProviders } from "../../test/render";

const navigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigate
  };
});

vi.mock("../../api/identity", () => ({
  listOrganizations: vi.fn().mockResolvedValue({
    items: [
      {
        id: "org-1",
        name: "Alluring Lens Studios",
        code: "ALS",
        is_active: true,
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z"
      }
    ],
    meta: { page: 1, page_size: 10, total: 1, pages: 1 }
  }),
  activateOrganization: vi.fn(),
  deactivateOrganization: vi.fn()
}));

describe("OrganizationListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders organizations and navigates to onboarding", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrganizationListPage />, ["/organizations"]);

    expect(screen.getByRole("heading", { name: "Organizations" })).toBeInTheDocument();
    expect(await screen.findByText("Alluring Lens Studios")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /new organization/i }));

    expect(navigate).toHaveBeenCalledWith("/organizations/new");
  });
});

