import type { GalleryStatus } from "../../types/galleries";

export const galleryStatuses: GalleryStatus[] = [
  "DRAFT",
  "UPLOADED",
  "SELECTION_OPEN",
  "SELECTION_CLOSED"
];

export function galleryStatusColor(status: GalleryStatus) {
  const colors: Record<GalleryStatus, string> = {
    DRAFT: "default",
    UPLOADED: "blue",
    SELECTION_OPEN: "green",
    SELECTION_CLOSED: "red"
  };
  return colors[status];
}

export function labelFromEnum(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(" ");
}

export function canManageGalleries(roleNames: string[]) {
  return roleNames.some((role) =>
    ["Super Admin", "Organization Admin", "Owner", "Branch Manager"].includes(role)
  );
}

export function canUploadGalleryPhotos(roleNames: string[]) {
  return roleNames.some((role) =>
    ["Super Admin", "Organization Admin", "Owner", "Branch Manager", "Photographer"].includes(role)
  );
}
