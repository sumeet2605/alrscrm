import { describe, expect, it } from "vitest";

import { canAccessPath } from "./routePermissions";

describe("routePermissions", () => {
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
    expect(canAccessPath(["Photographer"], "/delivery")).toBe(false);
    expect(canAccessPath([], "/client/delivery/delivery-1")).toBe(true);
  });
});
