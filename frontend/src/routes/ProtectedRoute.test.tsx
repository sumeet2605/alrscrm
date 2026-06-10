import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ProtectedRoute } from "./ProtectedRoute";
import { renderWithProviders } from "../test/render";

let authState = {
  user: null as null | { roles: { name: string }[] },
  isAuthenticated: false,
  isBootstrapping: false
};

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => authState
}));

describe("ProtectedRoute", () => {
  beforeEach(() => {
    authState = { user: null, isAuthenticated: false, isBootstrapping: false };
  });

  it("redirects unauthenticated users to login", () => {
    renderWithProviders(
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/users" element={<div>Users</div>} />
        </Route>
        <Route path="/login" element={<div>Login</div>} />
      </Routes>,
      ["/users"]
    );

    expect(screen.getByText("Login")).toBeInTheDocument();
  });

  it("allows owners to access user management", () => {
    authState = {
      user: { roles: [{ name: "Owner" }] },
      isAuthenticated: true,
      isBootstrapping: false
    };
    renderWithProviders(
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/users" element={<div>Users</div>} />
        </Route>
        <Route path="/dashboard" element={<div>Dashboard</div>} />
      </Routes>,
      ["/users"]
    );

    expect(screen.getByText("Users")).toBeInTheDocument();
  });
});
