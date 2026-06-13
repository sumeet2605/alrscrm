import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/render";
import { ClientDeliveryPage } from "./ClientDeliveryPage";

vi.mock("../../api/delivery", () => ({
  authenticateClientDelivery: vi.fn(async () => ({
    session_token: "delivery-session-token",
    expires_in_seconds: 86400
  })),
  downloadClientDelivery: vi.fn(),
  getClientDelivery: vi.fn(async () => ({
    id: "delivery-1",
    delivery_number: "DL-2026-000001",
    delivery_status: "SENT",
    zip_generation_status: "COMPLETED",
    edited_photo_count: 12,
    delivery_date: "2026-06-11",
    expiry_date: "2026-09-09",
    download_count: 1,
    max_downloads: 10,
    remaining_downloads: 9,
    allow_re_download: false,
    password_required: false,
    watermark_enabled: true,
    original_download_enabled: false,
    gallery_name: "Newborn Finals",
    booking_number: "BK-001"
  })),
  requestDeliveryReopen: vi.fn()
}));

describe("ClientDeliveryPage", () => {
  it("renders public delivery access", async () => {
    renderWithProviders(
      <Routes>
        <Route path="/client/delivery/:token" element={<ClientDeliveryPage />} />
      </Routes>,
      ["/client/delivery/secure-token"]
    );

    expect(await screen.findByText("DL-2026-000001")).toBeInTheDocument();
    expect(screen.getByText("Newborn Finals")).toBeInTheDocument();
    expect(screen.getByText("Downloads Remaining")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /download/i })).toBeEnabled();
  });
});
