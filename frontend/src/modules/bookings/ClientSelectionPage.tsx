import { HeartFilled, HeartOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Empty, Image, Input, Space, Typography } from "antd";
import { useMemo, useState, useEffect } from "react";
import { useParams } from "react-router-dom";

import {
  addPublicGalleryFavorite,
  getPublicGallery,
  authenticatePublicGallery,
} from "../../api/galleries";

export function ClientSelectionPage() {
  const { galleryId } = useParams();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [selectedByName, setSelectedByName] = useState("");
  const [selectedByEmail, setSelectedByEmail] = useState("");
  const [token, setToken] = useState<string | null>(null);
  useEffect(() => {
    if (galleryId) {
      const stored = localStorage.getItem(`gallery_access_${galleryId}`);
      if (stored) setToken(stored);
    }
  }, [galleryId]);
  const [password, setPassword] = useState("");
  const galleryQuery = useQuery({
    queryKey: ["public-gallery", galleryId, token],
    queryFn: () => getPublicGallery(galleryId!, token ?? undefined),
    enabled: Boolean(galleryId)
  });
  const selectedPhotoIds = useMemo(
    () => new Set((galleryQuery.data?.favorites ?? []).map((favorite) => favorite.gallery_photo_id)),
    [galleryQuery.data?.favorites]
  );
  const favoriteMutation = useMutation({
    mutationFn: (gallery_photo_id: string) =>
      addPublicGalleryFavorite(
        galleryId!,
        {
          gallery_photo_id,
          selected_by_name: selectedByName,
          selected_by_email: selectedByEmail || undefined,
        },
        token ?? undefined
      ),
    onSuccess: async () => {
      message.success("Favorite saved");
      await queryClient.invalidateQueries({ queryKey: ["public-gallery", galleryId, token] });
    }
  });
  const gallery = galleryQuery.data;
  const canSelect = gallery?.gallery_status === "SELECTION_OPEN" && !gallery?.selection_locked;
  const selectionLimit = gallery?.selection_limit ?? Infinity;
  const selectionCount = gallery?.selection_count ?? (gallery?.favorites.length ?? 0);

  const showAuth = Boolean(galleryQuery.isError);

  return (
    <main className="client-gallery-page">
      <div className="client-gallery-header">
        <div>
          <Typography.Title level={1}>{gallery?.gallery_name ?? "Gallery"}</Typography.Title>
          <Typography.Text type="secondary">
            Selected: {selectionCount} / {selectionLimit}
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

      {showAuth && (
        <div style={{ marginBottom: 16 }}>
          <Typography.Text type="danger">This gallery requires a password.</Typography.Text>
          <Space style={{ marginLeft: 8 }}>
            <Input.Password
              placeholder="Gallery password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button
              onClick={async () => {
                try {
                    const res = await authenticatePublicGallery(galleryId!, password);
                    localStorage.setItem(`gallery_access_${galleryId}`, res.access_token);
                    setToken(res.access_token);
                    setPassword("");
                    await queryClient.invalidateQueries({ queryKey: ["public-gallery", galleryId, res.access_token] });
                  message.success("Authenticated");
                } catch (err: any) {
                  message.error(err?.response?.data?.message ?? "Authentication failed");
                }
              }}
            >
              Authenticate
            </Button>
          </Space>
        </div>
      )}

      {gallery && gallery.photos.length > 0 ? (
        <div className="client-photo-grid">
          {gallery.photos.map((photo) => {
            const selected = selectedPhotoIds.has(photo.id);
            const limitReached = !selected && selectionCount >= selectionLimit;
            const disabled = !canSelect || !selectedByName || selected || limitReached;
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
                  disabled={disabled}
                  onClick={() => {
                    if (limitReached) {
                      message.error(
                        "Selection limit reached. Contact studio to purchase additional edited photos."
                      );
                      return;
                    }
                    favoriteMutation.mutate(photo.id);
                  }} />
                </div>
              );
            })}
        </div>
      ) : (
        <Empty description="No photos available" />
      )}
      {canSelect && (
        <div style={{ marginTop: 16 }}>
          <Button
            type="primary"
            onClick={async () => {
              try {
                const { submitPublicSelection } = await import("../../api/galleries");
                await submitPublicSelection(galleryId!, token ?? undefined);
                message.success("Selection submitted");
                await queryClient.invalidateQueries({ queryKey: ["public-gallery", galleryId, token] });
              } catch (err: any) {
                message.error(err?.response?.data?.message ?? "Failed to submit selection");
              }
            }}
          >
            Submit Final Selection
          </Button>
        </div>
      )}
    </main>
  );
}
