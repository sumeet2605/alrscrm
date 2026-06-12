import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { createInvoice } from "../../api/finance";
import { renderWithProviders } from "../../test/render";
import { InvoiceListPage } from "./InvoiceListPage";

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

vi.mock("../../api/identity", () => ({
  getOrganization: vi.fn(async () => ({
    id: "org-1",
    name: "ALR Studio",
    code: "ALR",
    is_active: true,
    created_at: "2026-06-10T00:00:00Z",
    updated_at: "2026-06-10T00:00:00Z"
  })),
  listBranches: vi.fn(async () => ({
    items: [
      {
        id: "branch-1",
        organization_id: "org-1",
        name: "Main Studio",
        code: "MAIN",
        city: "Mumbai",
        is_active: true,
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z"
      }
    ],
    meta: { page: 1, page_size: 100, total: 1, total_pages: 1 }
  }))
}));

vi.mock("../../api/finance", () => ({
  listInvoices: vi.fn(async () => ({
    items: [],
    meta: { page: 1, page_size: 10, total: 0, total_pages: 0 }
  })),
  createInvoice: vi.fn(async () => ({ id: "invoice-1" }))
}));

describe("InvoiceListPage", () => {
  it("shows organization and branch names while submitting ids", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InvoiceListPage />, ["/finance/invoices"]);

    await user.click(await screen.findByRole("button", { name: /new invoice/i }));
    const dialog = await screen.findByRole("dialog", { name: "Create Invoice" });

    expect(within(dialog).getByDisplayValue("ALR Studio")).toBeInTheDocument();
    expect(await within(dialog).findByText("Main Studio · Mumbai")).toBeInTheDocument();
    expect(within(dialog).queryByLabelText("Organization ID")).not.toBeInTheDocument();
    expect(within(dialog).queryByLabelText("Branch ID")).not.toBeInTheDocument();

    await user.type(within(dialog).getByLabelText("Family ID"), "family-1");
    await user.type(within(dialog).getByLabelText("Booking ID"), "booking-1");
    await user.type(within(dialog).getByLabelText("Buyer Billing Name"), "Sharma Family");
    await user.clear(within(dialog).getByLabelText("Line Price"));
    await user.type(within(dialog).getByLabelText("Line Price"), "25000");
    await user.click(within(dialog).getByRole("button", { name: "Create" }));

    await waitFor(() => {
      expect(createInvoice).toHaveBeenCalledWith(
        expect.objectContaining({
          organization_id: "org-1",
          branch_id: "branch-1",
          family_id: "family-1",
          booking_id: "booking-1",
          buyer_billing_name: "Sharma Family"
        })
      );
    });
  });
});
