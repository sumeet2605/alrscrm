import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { IntegrationsDashboardPage } from "./IntegrationsDashboardPage";

vi.mock("../../api/integrations", () => ({
  getIntegrationHealth: vi.fn(async () => ({
    connected: 1,
    disconnected: 1,
    expired: 0,
    error: 0
  })),
  listIntegrations: vi.fn(async () => ({
    items: [
      {
        id: "integration-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        provider: "SMTP_EMAIL",
        status: "CONNECTED",
        credential_keys: ["host", "username"],
        created_by_user_id: "user-1",
        created_at: "2026-06-11T00:00:00Z",
        updated_at: "2026-06-11T00:00:00Z"
      }
    ],
    meta: { page: 1, page_size: 50, total: 1, pages: 1 }
  })),
  verifyIntegration: vi.fn()
}));

describe("IntegrationsDashboardPage", () => {
  it("renders integration health and providers", async () => {
    renderWithProviders(<IntegrationsDashboardPage />);

    expect(await screen.findByText("Integrations")).toBeInTheDocument();
    expect(screen.getAllByText("Connected").length).toBeGreaterThan(0);
    expect(screen.getByText("Smtp Email")).toBeInTheDocument();
    expect(screen.getByText("host, username")).toBeInTheDocument();
  });
});
