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
  "Super Admin": fullAccessRoutes
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
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
