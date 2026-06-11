const fullAccessRoutes = [
  "/dashboard",
  "/families",
  "/sales",
  "/bookings",
  "/packages",
  "/galleries",
  "/schedules",
  "/production",
  "/delivery",
  "/branches",
  "/users",
  "/roles"
];

const platformRoutes = ["/organizations"];

export const roleRoutes: Record<string, string[]> = {
  Owner: fullAccessRoutes,
  "Organization Admin": fullAccessRoutes,
  "Branch Manager": [
    "/dashboard",
    "/families",
    "/sales",
    "/bookings",
    "/packages",
    "/galleries",
    "/schedules",
    "/production",
    "/delivery",
    "/users"
  ],
  "Sales Executive": ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  Photographer: ["/dashboard", "/families", "/sales", "/bookings", "/galleries", "/schedules"],
  Editor: [
    "/dashboard",
    "/families",
    "/sales",
    "/bookings",
    "/galleries",
    "/schedules",
    "/production",
    "/delivery"
  ],
  "Customer Success": [
    "/dashboard",
    "/families",
    "/sales",
    "/bookings",
    "/galleries",
    "/schedules",
    "/production"
  ],
  "Super Admin": [...platformRoutes, ...fullAccessRoutes]
};

export function canAccessPath(roleNames: string[], path: string): boolean {
  if (
    path === "/" ||
    path === "/login" ||
    path.startsWith("/client/galleries") ||
    path.startsWith("/client/delivery")
  ) {
    return true;
  }
  if (path.startsWith("/delivery/dashboard")) {
    return roleNames.some((role) =>
      ["Super Admin", "Organization Admin", "Owner", "Branch Manager"].includes(role)
    );
  }
  if (path.startsWith("/organizations")) {
    return roleNames.includes("Super Admin");
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
