export const roleRoutes: Record<string, string[]> = {
  Owner: ["/dashboard", "/families", "/branches", "/users", "/roles"],
  "Branch Manager": ["/dashboard", "/families", "/users"],
  "Sales Executive": ["/dashboard", "/families"],
  Photographer: ["/dashboard", "/families"],
  Editor: ["/dashboard", "/families"],
  "Customer Success": ["/dashboard", "/families"],
  "Super Admin": ["/dashboard", "/families", "/branches", "/users", "/roles"]
};

export function canAccessPath(roleNames: string[], path: string): boolean {
  if (path === "/" || path === "/login") {
    return true;
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
