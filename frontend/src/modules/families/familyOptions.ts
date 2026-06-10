import type { FamilyStatus, LeadSource, Relationship, ServiceType } from "../../types/families";

export const familyStatuses: FamilyStatus[] = ["INQUIRY", "INTERESTED", "BOOKED", "ACTIVE", "INACTIVE"];
export const leadSources: LeadSource[] = ["INSTAGRAM", "WHATSAPP", "GOOGLE", "REFERRAL", "WEBSITE", "WALKIN", "OTHER"];
export const relationships: Relationship[] = ["MOTHER", "FATHER", "BABY", "GRANDPARENT", "SIBLING", "OTHER"];
export const serviceTypes: ServiceType[] = ["MATERNITY", "NEWBORN", "FAMILY", "MILESTONE", "CAKE_SMASH"];

export function labelFromEnum(value: string): string {
  return value
    .split("_")
    .map((part) => `${part.slice(0, 1)}${part.slice(1).toLowerCase()}`)
    .join(" ");
}

export function familyStatusColor(status: FamilyStatus): string {
  const colors: Record<FamilyStatus, string> = {
    INQUIRY: "default",
    INTERESTED: "blue",
    BOOKED: "purple",
    ACTIVE: "green",
    INACTIVE: "red"
  };
  return colors[status];
}

export function canWriteFamilies(roleNames: string[]): boolean {
  return roleNames.some((role) =>
    ["Super Admin", "Owner", "Branch Manager", "Sales Executive"].includes(role)
  );
}

export function canDeleteFamilies(roleNames: string[]): boolean {
  return roleNames.some((role) => ["Super Admin", "Owner", "Branch Manager"].includes(role));
}
