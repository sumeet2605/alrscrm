export const roleRoutes: Record<string, string[]> = {
  Owner: ["/dashboard", "/branches", "/users", "/roles"],
  "Branch Manager": ["/dashboard", "/users"],
  "Sales Executive": ["/dashboard"],
  Photographer: ["/dashboard"],
  Editor: ["/dashboard"],
  "Customer Success": ["/dashboard"],
  "Super Admin": ["/dashboard", "/branches", "/users", "/roles"]
};

export function canAccessPath(roleNames: string[], path: string): boolean {
  if (path === "/" || path === "/login") {
    return true;
  }
  return roleNames.some((role) => roleRoutes[role]?.some((route) => path.startsWith(route)));
}
