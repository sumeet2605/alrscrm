const fullAccessRoutes = [
  "/dashboard",
  "/families",
  "/sales",
  "/bookings",
  "/packages",
  "/galleries",
  "/schedules",
  "/production",
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
    "/users"
  ],
  "Sales Executive": ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  Photographer: ["/dashboard", "/families", "/sales", "/bookings", "/galleries", "/schedules"],
  Editor: ["/dashboard", "/families", "/sales", "/bookings", "/galleries", "/schedules", "/production"],
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
  if (path === "/" || path === "/login" || path.startsWith("/client/galleries")) {
    return true;
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
