import { describe, expect, it } from "vitest";

import { canAccessPath } from "./routePermissions";

describe("routePermissions", () => {
  it("allows organization management only for Super Admin", () => {
    expect(canAccessPath(["Super Admin"], "/organizations")).toBe(true);
    expect(canAccessPath(["Super Admin"], "/organizations/new")).toBe(true);
    expect(canAccessPath(["Organization Admin"], "/organizations")).toBe(false);
    expect(canAccessPath(["Owner"], "/organizations/new")).toBe(false);
  });

  it("allows package management only for administrative booking roles", () => {
    expect(canAccessPath(["Super Admin"], "/packages")).toBe(true);
    expect(canAccessPath(["Organization Admin"], "/packages")).toBe(true);
    expect(canAccessPath(["Branch Manager"], "/packages")).toBe(true);
    expect(canAccessPath(["Photographer"], "/packages")).toBe(false);
    expect(canAccessPath(["Editor"], "/packages")).toBe(false);
  });

  it("allows gallery access to fulfillment roles and public client links", () => {
    expect(canAccessPath(["Super Admin"], "/galleries")).toBe(true);
    expect(canAccessPath(["Branch Manager"], "/galleries")).toBe(true);
    expect(canAccessPath(["Photographer"], "/galleries")).toBe(true);
    expect(canAccessPath(["Client"], "/galleries")).toBe(false);
    expect(canAccessPath([], "/client/galleries/gallery-1")).toBe(true);
  });

  it("allows production access to managers, customer success, and editors", () => {
    expect(canAccessPath(["Super Admin"], "/production")).toBe(true);
    expect(canAccessPath(["Organization Admin"], "/production/editing")).toBe(true);
    expect(canAccessPath(["Branch Manager"], "/production/editor-dashboard")).toBe(true);
    expect(canAccessPath(["Editor"], "/production/editing/job-1")).toBe(true);
    expect(canAccessPath(["Customer Success"], "/production")).toBe(true);
    expect(canAccessPath(["Photographer"], "/production")).toBe(false);
  });

  it("allows delivery access to managers and editors plus public client links", () => {
    expect(canAccessPath(["Super Admin"], "/delivery")).toBe(true);
    expect(canAccessPath(["Organization Admin"], "/delivery/dashboard")).toBe(true);
    expect(canAccessPath(["Branch Manager"], "/delivery/job-1")).toBe(true);
    expect(canAccessPath(["Editor"], "/delivery/job-1")).toBe(true);
    expect(canAccessPath(["Editor"], "/delivery/dashboard")).toBe(false);
    expect(canAccessPath(["Photographer"], "/delivery")).toBe(false);
    expect(canAccessPath([], "/client/delivery/delivery-1")).toBe(true);
  });

  it("allows finance access only to administrative finance roles", () => {
    expect(canAccessPath(["Super Admin"], "/finance")).toBe(true);
    expect(canAccessPath(["Owner"], "/finance/invoices")).toBe(true);
    expect(canAccessPath(["Organization Admin"], "/finance/payments/payment-1")).toBe(true);
    expect(canAccessPath(["Branch Manager"], "/finance/invoices/invoice-1")).toBe(true);
    expect(canAccessPath(["Sales Executive"], "/finance")).toBe(false);
    expect(canAccessPath(["Photographer"], "/finance/payments")).toBe(false);
    expect(canAccessPath(["Editor"], "/finance/invoices")).toBe(false);
  });

  it("allows integration settings only to administrative tenant roles", () => {
    expect(canAccessPath(["Super Admin"], "/settings/integrations")).toBe(true);
    expect(canAccessPath(["Owner"], "/settings/integrations/email")).toBe(true);
    expect(canAccessPath(["Organization Admin"], "/settings/integrations/storage")).toBe(true);
    expect(canAccessPath(["Branch Manager"], "/settings/integrations/whatsapp")).toBe(true);
    expect(canAccessPath(["Photographer"], "/settings/integrations")).toBe(false);
    expect(canAccessPath(["Editor"], "/settings/integrations")).toBe(false);
  });
});
