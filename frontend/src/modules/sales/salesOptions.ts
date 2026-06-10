import type { FollowUpStatus, FollowUpType, OpportunityStage, OpportunityType } from "../../types/sales";

export const opportunityStages: OpportunityStage[] = [
  "NEW",
  "PACKAGE_SENT",
  "INTERESTED",
  "NEED_FOLLOW_UP",
  "THINKING",
  "BOOKED",
  "LOST"
];

export const opportunityTypes: OpportunityType[] = [
  "MATERNITY",
  "NEWBORN",
  "FAMILY",
  "MILESTONE",
  "CAKE_SMASH"
];

export const followUpTypes: FollowUpType[] = ["CALL", "WHATSAPP", "INSTAGRAM_DM", "EMAIL", "OTHER"];
export const followUpStatuses: FollowUpStatus[] = ["PENDING", "COMPLETED", "MISSED"];

export function labelFromEnum(value: string): string {
  return value
    .split("_")
    .map((part) => `${part.slice(0, 1)}${part.slice(1).toLowerCase()}`)
    .join(" ");
}

export function stageColor(stage: OpportunityStage): string {
  const colors: Record<OpportunityStage, string> = {
    NEW: "default",
    PACKAGE_SENT: "blue",
    INTERESTED: "cyan",
    NEED_FOLLOW_UP: "gold",
    THINKING: "orange",
    BOOKED: "green",
    LOST: "red"
  };
  return colors[stage];
}

export function canWriteSales(roleNames: string[]): boolean {
  return roleNames.some((role) =>
    ["Super Admin", "Owner", "Branch Manager", "Sales Executive"].includes(role)
  );
}

export function canDeleteSales(roleNames: string[]): boolean {
  return roleNames.some((role) => ["Super Admin", "Owner", "Branch Manager"].includes(role));
}
