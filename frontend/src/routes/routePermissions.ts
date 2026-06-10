export const roleRoutes: Record<string, string[]> = {
  Owner: ["/dashboard", "/families", "/sales", "/branches", "/users", "/roles"],
  "Branch Manager": ["/dashboard", "/families", "/sales", "/users"],
  "Sales Executive": ["/dashboard", "/families", "/sales"],
  Photographer: ["/dashboard", "/families", "/sales"],
  Editor: ["/dashboard", "/families", "/sales"],
  "Customer Success": ["/dashboard", "/families", "/sales"],
  "Super Admin": ["/dashboard", "/families", "/sales", "/branches", "/users", "/roles"]
};

export function canAccessPath(roleNames: string[], path: string): boolean {
  if (path === "/" || path === "/login") {
    return true;
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
