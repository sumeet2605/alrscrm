export const roleRoutes: Record<string, string[]> = {
  Owner: ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/galleries", "/schedules", "/branches", "/users", "/roles"],
  "Organization Admin": ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/galleries", "/schedules", "/branches", "/users", "/roles"],
  "Branch Manager": ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/galleries", "/schedules", "/users"],
  "Sales Executive": ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  Photographer: ["/dashboard", "/families", "/sales", "/bookings", "/galleries", "/schedules"],
  Editor: ["/dashboard", "/families", "/sales", "/bookings", "/galleries", "/schedules"],
  "Customer Success": ["/dashboard", "/families", "/sales", "/bookings", "/galleries", "/schedules"],
  "Super Admin": ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/galleries", "/schedules", "/branches", "/users", "/roles"]
};

export function canAccessPath(roleNames: string[], path: string): boolean {
  if (path === "/" || path === "/login" || path.startsWith("/client/galleries")) {
    return true;
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
