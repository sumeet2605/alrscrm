import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DashboardLayout } from "./DashboardLayout";
import { renderWithProviders } from "../test/render";

let roleNames = ["Branch Manager"];

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      id: "user-1",
      organization_id: "org-1",
      branch_id: "branch-1",
      email: "manager@example.com",
      first_name: "Branch",
      last_name: "Manager",
      roles: roleNames.map((name) => ({ id: name, name }))
    },
    logout: vi.fn()
  })
}));

describe("DashboardLayout", () => {
  beforeEach(() => {
    roleNames = ["Branch Manager"];
  });

  it("navigates to package management from the bookings menu", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<div>Dashboard Route</div>} />
          <Route path="/packages" element={<div>Package Management Route</div>} />
        </Route>
      </Routes>,
      ["/dashboard"]
    );

    expect(screen.getAllByText("Bookings").length).toBeGreaterThan(0);
    await user.click(screen.getByText("Package Management"));

    expect(screen.getByText("Package Management Route")).toBeInTheDocument();
  });

  it("hides package management from photographers", () => {
    roleNames = ["Photographer"];
    renderWithProviders(
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<div>Dashboard Route</div>} />
        </Route>
      </Routes>,
      ["/dashboard"]
    );

    expect(screen.queryByText("Package Management")).not.toBeInTheDocument();
  });
});
