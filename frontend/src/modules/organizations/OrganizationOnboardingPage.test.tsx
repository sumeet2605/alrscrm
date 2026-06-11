import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { onboardOrganization } from "../../api/identity";
import { renderWithProviders } from "../../test/render";
import { OrganizationOnboardingPage } from "./OrganizationOnboardingPage";

const navigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigate
  };
});

vi.mock("../../api/identity", () => ({
  onboardOrganization: vi.fn().mockResolvedValue({
    organization: {
      id: "org-1",
      name: "Alluring Lens Studios",
      code: "ALS",
      is_active: true,
      created_at: "2026-06-10T00:00:00Z",
      updated_at: "2026-06-10T00:00:00Z"
    },
    settings: {
      id: "settings-1",
      organization_id: "org-1",
      studio_name: "Alluring Lens Studios",
      timezone: "Asia/Kolkata",
      currency: "INR",
      delivery_expiry_default: 30,
      gallery_selection_default_limit: 30,
      created_at: "2026-06-10T00:00:00Z",
      updated_at: "2026-06-10T00:00:00Z"
    },
    branch_id: "branch-1",
    owner_id: "owner-1",
    owner_temporary_password: "TempPassword123"
  })
}));

describe("OrganizationOnboardingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("submits the organization onboarding wizard", async () => {
    const user = userEvent.setup();
    renderWithProviders(<OrganizationOnboardingPage />, ["/organizations/new"]);

    await user.type(screen.getByLabelText("Organization Name"), "Alluring Lens Studios");
    await user.type(screen.getByLabelText("Organization Code"), "ALS");
    await user.type(screen.getByLabelText("Email"), "hello@alluringlens.com");
    await user.type(screen.getByLabelText("Phone"), "+91 90000 00000");
    await user.click(screen.getByRole("button", { name: "Next" }));

    expect(screen.getByLabelText("Branch Name")).toHaveValue("Main Studio");
    await user.click(screen.getByRole("button", { name: "Next" }));

    await user.type(screen.getByLabelText("Owner Name"), "Studio Owner");
    await user.type(screen.getByLabelText("Owner Email"), "owner@alluringlens.com");
    await user.type(screen.getByLabelText("Owner Phone"), "+91 90000 00001");
    await user.click(screen.getByRole("button", { name: "Next" }));

    await user.click(screen.getByRole("button", { name: /create organization/i }));

    expect(onboardOrganization).toHaveBeenCalledWith({
      organization: {
        name: "Alluring Lens Studios",
        code: "ALS",
        timezone: "Asia/Kolkata",
        email: "hello@alluringlens.com",
        phone: "+91 90000 00000"
      },
      branch: { name: "Main Studio" },
      owner: {
        name: "Studio Owner",
        email: "owner@alluringlens.com",
        phone: "+91 90000 00001"
      }
    });
    expect(await screen.findByText("Organization created")).toBeInTheDocument();
    expect(screen.getByText("TempPassword123")).toBeInTheDocument();
  });
});
