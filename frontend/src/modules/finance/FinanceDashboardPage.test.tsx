import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { FinanceDashboardPage } from "./FinanceDashboardPage";

vi.mock("../../api/finance", () => ({
  getFinanceMetrics: vi.fn(async () => ({
    revenue_this_month: "5000.00",
    revenue_this_year: "5000.00",
    outstanding_amount: "6800.00",
    paid_amount: "5000.00",
    overdue_amount: "0.00",
    invoices_by_status: {
      PARTIALLY_PAID: 1
    },
    payments_by_method: {
      UPI: 1
    }
  }))
}));

describe("FinanceDashboardPage", () => {
  it("renders finance metrics", async () => {
    renderWithProviders(<FinanceDashboardPage />);

    expect(await screen.findByText("Finance Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Outstanding")).toBeInTheDocument();
    expect(screen.getByText("Invoices By Status")).toBeInTheDocument();
    expect(screen.getByText("Payments By Method")).toBeInTheDocument();
  });
});
