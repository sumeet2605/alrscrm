import { DeleteOutlined, InboxOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Image, Progress, Space, Table, Typography, Upload } from "antd";
import type { RcFile } from "antd/es/upload";
import { useState } from "react";
import { useParams } from "react-router-dom";

import { deleteGalleryPhoto, getGallery, uploadGalleryPhoto } from "../../api/galleries";

function getImageDimensions(src: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve) => {
    const image = new window.Image();
    image.onload = () => resolve({ width: image.naturalWidth || 1, height: image.naturalHeight || 1 });
    image.onerror = () => resolve({ width: 1, height: 1 });
    image.src = src;
  });
}

export function GalleryUploadPage() {
  const { galleryId } = useParams();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const [progress, setProgress] = useState(0);
  const galleryQuery = useQuery({
    queryKey: ["gallery", galleryId],
    queryFn: () => getGallery(galleryId!),
    enabled: Boolean(galleryId)
  });
  const uploadMutation = useMutation({
    mutationFn: async (file: RcFile) => {
      setProgress(35);
      const objectUrl = URL.createObjectURL(file);
      const dimensions = await getImageDimensions(objectUrl);
      URL.revokeObjectURL(objectUrl);
      setProgress(72);
      return uploadGalleryPhoto(galleryId!, file, {
        image_width: dimensions.width,
        image_height: dimensions.height
      });
    },
    onSuccess: async () => {
      setProgress(100);
      message.success("Photo uploaded");
      await queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
      setTimeout(() => setProgress(0), 500);
    }
  });
  const deleteMutation = useMutation({
    mutationFn: (photoId: string) => deleteGalleryPhoto(galleryId!, photoId),
    onSuccess: async () => {
      message.success("Photo deleted");
      await queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
    }
  });

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Upload Photos</Typography.Title>
          <Typography.Text type="secondary">
            {galleryQuery.data?.gallery_name ?? "Gallery upload"}
          </Typography.Text>
        </div>
      </div>

      <Upload.Dragger
        multiple
        showUploadList={false}
        customRequest={({ file, onSuccess }) => {
          uploadMutation.mutate(file as RcFile);
          onSuccess?.("ok");
        }}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Drop photos here or click to upload</p>
      </Upload.Dragger>

      {progress > 0 && <Progress percent={progress} />}

      <Table
        rowKey="id"
        dataSource={galleryQuery.data?.photos ?? []}
        loading={galleryQuery.isLoading}
        columns={[
          {
            title: "Preview",
            render: (_, photo) => (
              <Image
                width={84}
                height={64}
                src={photo.thumbnail_path ?? photo.storage_path}
                fallback="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
              />
            )
          },
          { title: "File", dataIndex: "file_name" },
          { title: "Size", dataIndex: "file_size", render: (value) => `${Math.round(value / 1024)} KB` },
          {
            title: "Actions",
            render: (_, photo) => (
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={() => deleteMutation.mutate(photo.id)}
              />
            )
          }
        ]}
      />
    </Space>
  );
}
