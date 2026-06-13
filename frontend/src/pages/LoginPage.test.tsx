import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { LoginPage } from "./LoginPage";
import { renderWithProviders } from "../test/render";

const loginMock = vi.fn();

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    login: loginMock,
    isAuthenticated: false,
    user: null
  })
}));

describe("LoginPage", () => {
  beforeEach(() => {
    loginMock.mockReset();
  });

  it("submits valid credentials and shows loading-safe form controls", async () => {
    loginMock.mockResolvedValue(undefined);
    renderWithProviders(<LoginPage />, ["/login"]);

    fireEvent.change(screen.getByLabelText("Organization Code"), {
      target: { value: "ALRSCRM" }
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "admin@admin.com" }
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "Admin@123" }
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(loginMock).toHaveBeenCalledWith({
        organization_code: "ALRSCRM",
        email: "admin@admin.com",
        password: "Admin@123"
      });
    });
  });

  it("renders backend login errors", async () => {
    loginMock.mockRejectedValue(new Error("Invalid email or password"));
    renderWithProviders(<LoginPage />, ["/login"]);

    fireEvent.change(screen.getByLabelText("Organization Code"), {
      target: { value: "ALRSCRM" }
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "wrong@example.com" }
    });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "bad" }
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText("Invalid email or password")).toBeInTheDocument();
  });
});
