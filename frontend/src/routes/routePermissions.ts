export const roleRoutes: Record<string, string[]> = {
  Owner: ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/schedules", "/branches", "/users", "/roles"],
  "Branch Manager": ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/schedules", "/users"],
  "Sales Executive": ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  Photographer: ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  Editor: ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  "Customer Success": ["/dashboard", "/families", "/sales", "/bookings", "/schedules"],
  "Super Admin": ["/dashboard", "/families", "/sales", "/bookings", "/packages", "/schedules", "/branches", "/users", "/roles"]
};

export function canAccessPath(roleNames: string[], path: string): boolean {
  if (path === "/" || path === "/login") {
    return true;
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
