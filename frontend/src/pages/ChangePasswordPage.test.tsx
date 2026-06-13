import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChangePasswordPage } from "./ChangePasswordPage";
import { renderWithProviders } from "../test/render";

const changePasswordMock = vi.fn();

let authState = {
  user: {
    email: "owner@example.com",
    password_reset_required: false
  },
  changePassword: changePasswordMock
};

vi.mock("../contexts/AuthContext", () => ({
  useAuth: () => authState
}));

describe("ChangePasswordPage", () => {
  beforeEach(() => {
    changePasswordMock.mockReset();
    authState = {
      user: {
        email: "owner@example.com",
        password_reset_required: false
      },
      changePassword: changePasswordMock
    };
  });

  it("submits current and new password", async () => {
    changePasswordMock.mockResolvedValue(undefined);
    renderWithProviders(<ChangePasswordPage />, ["/change-password"]);

    fireEvent.change(screen.getByLabelText("Current Password"), {
      target: { value: "StrongPass123" }
    });
    fireEvent.change(screen.getByLabelText("New Password"), {
      target: { value: "NewStrongPass123" }
    });
    fireEvent.change(screen.getByLabelText("Confirm Password"), {
      target: { value: "NewStrongPass123" }
    });
    fireEvent.click(screen.getByRole("button", { name: /save password/i }));

    await waitFor(() => {
      expect(changePasswordMock).toHaveBeenCalledWith({
        current_password: "StrongPass123",
        new_password: "NewStrongPass123"
      });
    });
  });

  it("shows forced reset state", () => {
    authState = {
      user: {
        email: "owner@example.com",
        password_reset_required: true
      },
      changePassword: changePasswordMock
    };

    renderWithProviders(<ChangePasswordPage />, ["/change-password"]);

    expect(screen.getByText("Password change required")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /back/i })).not.toBeInTheDocument();
  });

  it("renders backend change errors", async () => {
    changePasswordMock.mockRejectedValue(new Error("Current password is incorrect"));
    renderWithProviders(<ChangePasswordPage />, ["/change-password"]);

    fireEvent.change(screen.getByLabelText("Current Password"), {
      target: { value: "WrongPass123" }
    });
    fireEvent.change(screen.getByLabelText("New Password"), {
      target: { value: "NewStrongPass123" }
    });
    fireEvent.change(screen.getByLabelText("Confirm Password"), {
      target: { value: "NewStrongPass123" }
    });
    fireEvent.click(screen.getByRole("button", { name: /save password/i }));

    expect(await screen.findByText("Current password is incorrect")).toBeInTheDocument();
  });
});
