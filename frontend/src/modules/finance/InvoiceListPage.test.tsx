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

vi.mock("../../api/families", () => ({
  listFamilies: vi.fn(async () => ({
    items: [
      {
        id: "family-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        family_code: "FAM-001",
        primary_contact_name: "Sharma Family",
        primary_contact_phone: "+91 90000 00001",
        primary_contact_email: "sharma@example.com",
        city: "Mumbai",
        source: "INSTAGRAM",
        status: "BOOKED",
        created_at: "2026-06-10T00:00:00Z",
        updated_at: "2026-06-10T00:00:00Z",
        members: [],
        address: {
          id: "address-1",
          address_line_1: "12 Studio Road",
          address_line_2: null,
          city: "Mumbai",
          state: "Maharashtra",
          country: "India",
          postal_code: "400001",
          created_at: "2026-06-10T00:00:00Z",
          updated_at: "2026-06-10T00:00:00Z"
        },
        service_interests: []
      }
    ],
    meta: { page: 1, page_size: 100, total: 1, total_pages: 1 }
  }))
}));

vi.mock("../../api/bookings", () => ({
  listBookings: vi.fn(async () => ({
    items: [
      {
        id: "booking-1",
        organization_id: "org-1",
        branch_id: "branch-1",
        family_id: "family-1",
        opportunity_id: "opportunity-1",
        booking_number: "BK-001",
        booking_status: "CONFIRMED",
        total_amount: "25000.00",
        advance_received: "0.00",
        balance_amount: "25000.00",
        booking_date: "2026-06-12",
        created_at: "2026-06-12T00:00:00Z",
        updated_at: "2026-06-12T00:00:00Z",
        family: {
          id: "family-1",
          family_code: "FAM-001",
          primary_contact_name: "Sharma Family",
          primary_contact_phone: "+91 90000 00001",
          primary_contact_email: "sharma@example.com",
          city: "Mumbai"
        },
        opportunity: {
          id: "opportunity-1",
          opportunity_type: "NEWBORN",
          current_stage: "BOOKED",
          estimated_value: "25000.00"
        },
        items: [
          {
            id: "item-1",
            booking_id: "booking-1",
            package_id: "package-1",
            service_type: "NEWBORN",
            price: "25000.00",
            discount: "0.00",
            final_amount: "25000.00",
            status: "PENDING",
            created_at: "2026-06-12T00:00:00Z",
            updated_at: "2026-06-12T00:00:00Z",
            package: {
              id: "package-1",
              organization_id: "org-1",
              branch_id: "branch-1",
              name: "Newborn Signature",
              service_type: "NEWBORN",
              price: "25000.00",
              is_active: true,
              created_at: "2026-06-10T00:00:00Z",
              updated_at: "2026-06-10T00:00:00Z"
            },
            addons: []
          }
        ]
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

    await user.click(within(dialog).getByLabelText("Family"));
    await user.click(await screen.findByText("FAM-001 · Sharma Family · +91 90000 00001"));
    await user.click(within(dialog).getByLabelText("Booking"));
    await user.click(await screen.findByText("BK-001 · Sharma Family · ₹25,000.00"));

    expect(within(dialog).getByDisplayValue("Sharma Family")).toBeInTheDocument();
    expect(within(dialog).getByDisplayValue("12 Studio Road, Mumbai, Maharashtra, India, 400001")).toBeInTheDocument();
    expect(within(dialog).getByDisplayValue("Newborn Signature")).toBeInTheDocument();
    expect(within(dialog).getByDisplayValue("25000.00")).toBeInTheDocument();
    await user.click(within(dialog).getByRole("button", { name: "Create" }));

    await waitFor(() => {
      expect(createInvoice).toHaveBeenCalledWith(
        expect.objectContaining({
          organization_id: "org-1",
          branch_id: "branch-1",
          family_id: "family-1",
          booking_id: "booking-1",
          buyer_billing_name: "Sharma Family",
          line_items: [
            expect.objectContaining({
              description: "Newborn Signature",
              service_type: "NEWBORN",
              unit_price: "25000.00"
            })
          ]
        })
      );
    });
  });
});
