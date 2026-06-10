import { HeartFilled, HeartOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Empty, Image, Input, Space, Typography } from "antd";
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { addPublicGalleryFavorite, getPublicGallery } from "../../api/galleries";

export function ClientSelectionPage() {
  const { galleryId } = useParams();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [selectedByName, setSelectedByName] = useState("");
  const [selectedByEmail, setSelectedByEmail] = useState("");
  const galleryQuery = useQuery({
    queryKey: ["public-gallery", galleryId],
    queryFn: () => getPublicGallery(galleryId!),
    enabled: Boolean(galleryId)
  });
  const selectedPhotoIds = useMemo(
    () => new Set((galleryQuery.data?.favorites ?? []).map((favorite) => favorite.gallery_photo_id)),
    [galleryQuery.data?.favorites]
  );
  const favoriteMutation = useMutation({
    mutationFn: (gallery_photo_id: string) =>
      addPublicGalleryFavorite(galleryId!, {
        gallery_photo_id,
        selected_by_name: selectedByName,
        selected_by_email: selectedByEmail || undefined
      }),
    onSuccess: async () => {
      message.success("Favorite saved");
      await queryClient.invalidateQueries({ queryKey: ["public-gallery", galleryId] });
    }
  });
  const gallery = galleryQuery.data;
  const canSelect = gallery?.gallery_status === "SELECTION_OPEN";

  return (
    <main className="client-gallery-page">
      <div className="client-gallery-header">
        <div>
          <Typography.Title level={1}>{gallery?.gallery_name ?? "Gallery"}</Typography.Title>
          <Typography.Text type="secondary">
            Selected: {gallery?.favorites.length ?? 0} / {gallery?.photos.length ?? 0}
          </Typography.Text>
        </div>
        <Space>
          <Input
            placeholder="Your name"
            value={selectedByName}
            onChange={(event) => setSelectedByName(event.target.value)}
          />
          <Input
            placeholder="Email"
            value={selectedByEmail}
            onChange={(event) => setSelectedByEmail(event.target.value)}
          />
        </Space>
      </div>

      {gallery && gallery.photos.length > 0 ? (
        <div className="client-photo-grid">
          {gallery.photos.map((photo) => {
            const selected = selectedPhotoIds.has(photo.id);
            return (
              <div className="client-photo-tile" key={photo.id}>
                <Image
                  src={photo.thumbnail_path ?? photo.storage_path}
                  fallback="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
                />
                <Button
                  shape="circle"
                  className="favorite-button"
                  icon={selected ? <HeartFilled /> : <HeartOutlined />}
                  disabled={!canSelect || !selectedByName || selected}
                  onClick={() => favoriteMutation.mutate(photo.id)}
                />
              </div>
            );
          })}
        </div>
      ) : (
        <Empty description="No photos available" />
      )}
    </main>
  );
}
