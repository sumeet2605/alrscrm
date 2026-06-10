import { apiClient } from "./http";
import type { ApiEnvelope } from "../types/api";
import type {
  FavoritePayload,
  FavoriteSelection,
  Gallery,
  GalleryDetail,
  GalleryListParams,
  GalleryListResult,
  GalleryMetrics,
  GalleryPayload,
  GalleryPhoto,
  GalleryPhotoPayload,
  GalleryUpdatePayload
} from "../types/galleries";

export async function listGalleries(params: GalleryListParams): Promise<GalleryListResult> {
  const response = await apiClient.get<ApiEnvelope<Gallery[]>>("/galleries", { params });
  return { items: response.data.data, meta: response.data.meta! };
}

export async function getGallery(id: string): Promise<GalleryDetail> {
  const response = await apiClient.get<ApiEnvelope<GalleryDetail>>(`/galleries/${id}`);
  return response.data.data;
}

export async function createGallery(payload: GalleryPayload): Promise<GalleryDetail> {
  const response = await apiClient.post<ApiEnvelope<GalleryDetail>>("/galleries", payload);
  return response.data.data;
}

export async function updateGallery(
  id: string,
  payload: GalleryUpdatePayload
): Promise<GalleryDetail> {
  const response = await apiClient.put<ApiEnvelope<GalleryDetail>>(`/galleries/${id}`, payload);
  return response.data.data;
}

export async function listGalleryPhotos(id: string): Promise<GalleryPhoto[]> {
  const response = await apiClient.get<ApiEnvelope<GalleryPhoto[]>>(`/galleries/${id}/photos`);
  return response.data.data;
}

export async function addGalleryPhoto(
  id: string,
  payload: GalleryPhotoPayload
): Promise<GalleryPhoto> {
  const response = await apiClient.post<ApiEnvelope<GalleryPhoto>>(
    `/galleries/${id}/photos`,
    payload
  );
  return response.data.data;
}

export async function uploadGalleryPhoto(
  id: string,
  file: File,
  dimensions: { image_width: number; image_height: number }
): Promise<GalleryPhoto> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("image_width", String(dimensions.image_width));
  formData.append("image_height", String(dimensions.image_height));
  const response = await apiClient.post<ApiEnvelope<GalleryPhoto>>(
    `/galleries/${id}/photos/upload`,
    formData
  );
  return response.data.data;
}

export async function deleteGalleryPhoto(id: string, photoId: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(`/galleries/${id}/photos/${photoId}`);
}

export async function listGalleryFavorites(id: string): Promise<FavoriteSelection[]> {
  const response = await apiClient.get<ApiEnvelope<FavoriteSelection[]>>(
    `/galleries/${id}/favorites`
  );
  return response.data.data;
}

export async function addGalleryFavorite(
  id: string,
  payload: FavoritePayload
): Promise<FavoriteSelection> {
  const response = await apiClient.post<ApiEnvelope<FavoriteSelection>>(
    `/galleries/${id}/favorites`,
    payload
  );
  return response.data.data;
}

export async function deleteGalleryFavorite(id: string, favoriteId: string): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(
    `/galleries/${id}/favorites/${favoriteId}`
  );
}

export async function getGalleryMetrics(): Promise<GalleryMetrics> {
  const response = await apiClient.get<ApiEnvelope<GalleryMetrics>>("/galleries/metrics");
  return response.data.data;
}

export async function getPublicGallery(id: string): Promise<GalleryDetail> {
  const response = await apiClient.get<ApiEnvelope<GalleryDetail>>(`/galleries/${id}/public`);
  return response.data.data;
}

export async function addPublicGalleryFavorite(
  id: string,
  payload: FavoritePayload
): Promise<FavoriteSelection> {
  const response = await apiClient.post<ApiEnvelope<FavoriteSelection>>(
    `/galleries/${id}/public/favorites`,
    payload
  );
  return response.data.data;
}

export async function deletePublicGalleryFavorite(
  id: string,
  favoriteId: string
): Promise<void> {
  await apiClient.delete<ApiEnvelope<Record<string, never>>>(
    `/galleries/${id}/public/favorites/${favoriteId}`
  );
}
