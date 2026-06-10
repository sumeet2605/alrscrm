import { LinkOutlined, UploadOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Descriptions, Empty, Image, Select, Space, Table, Tag, Typography } from "antd";
import { useNavigate, useParams } from "react-router-dom";

import { getGallery, updateGallery } from "../../api/galleries";
import type { GalleryStatus } from "../../types/galleries";
import { galleryStatusColor, galleryStatuses, labelFromEnum } from "./galleryOptions";

export function GalleryDetailsPage() {
  const { galleryId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const galleryQuery = useQuery({
    queryKey: ["gallery", galleryId],
    queryFn: () => getGallery(galleryId!),
    enabled: Boolean(galleryId)
  });
  const statusMutation = useMutation({
    mutationFn: (gallery_status: GalleryStatus) => updateGallery(galleryId!, { gallery_status }),
    onSuccess: async () => {
      message.success("Gallery status updated");
      await queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
      await queryClient.invalidateQueries({ queryKey: ["galleries"] });
    }
  });
  const gallery = galleryQuery.data;

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{gallery?.gallery_name ?? "Gallery"}</Typography.Title>
          <Typography.Text type="secondary">
            {gallery?.booking_number} · {gallery?.family_name}
          </Typography.Text>
        </div>
        <Space>
          <Button icon={<LinkOutlined />} onClick={() => navigate(`/client/galleries/${galleryId}`)}>
            Public View
          </Button>
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => navigate(`/galleries/${galleryId}/upload`)}
          >
            Upload Photos
          </Button>
        </Space>
      </div>

      {gallery ? (
        <>
          <Descriptions bordered column={{ xs: 1, md: 3 }}>
            <Descriptions.Item label="Status">
              <Tag color={galleryStatusColor(gallery.gallery_status)}>
                {labelFromEnum(gallery.gallery_status)}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Photo Count">{gallery.photo_count}</Descriptions.Item>
            <Descriptions.Item label="Favorites">{gallery.favorite_count}</Descriptions.Item>
            <Descriptions.Item label="Change Status">
              <Select
                value={gallery.gallery_status}
                className="full-width-control"
                options={galleryStatuses.map((status) => ({
                  value: status,
                  label: labelFromEnum(status)
                }))}
                onChange={(value) => statusMutation.mutate(value)}
              />
            </Descriptions.Item>
          </Descriptions>

          <Table
            rowKey="id"
            title={() => "Photos"}
            dataSource={gallery.photos}
            pagination={false}
            columns={[
              {
                title: "Preview",
                render: (_, photo) => (
                  <Image
                    width={72}
                    height={54}
                    src={photo.thumbnail_path ?? photo.storage_path}
                    fallback="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
                  />
                )
              },
              { title: "File", dataIndex: "file_name" },
              { title: "Size", dataIndex: "file_size", render: (value) => `${Math.round(value / 1024)} KB` },
              { title: "Dimensions", render: (_, photo) => `${photo.image_width} x ${photo.image_height}` }
            ]}
            locale={{ emptyText: <Empty description="No photos uploaded" /> }}
          />

          <Table
            rowKey="id"
            title={() => "Favorites"}
            dataSource={gallery.favorites}
            pagination={false}
            columns={[
              { title: "Selected By", dataIndex: "selected_by_name" },
              { title: "Email", dataIndex: "selected_by_email" },
              { title: "Photo", render: (_, favorite) => favorite.gallery_photo?.file_name }
            ]}
          />
        </>
      ) : null}
    </Space>
  );
}
