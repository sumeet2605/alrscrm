import { DeleteOutlined, InboxOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Image, Progress, Space, Table, Tag, Typography, Upload } from "antd";
import type { RcFile } from "antd/es/upload";
import { useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";

import { deleteGalleryPhoto, getGallery, uploadGalleryPhoto } from "../../api/galleries";

type GalleryUploadFile = RcFile | { originFileObj?: RcFile };
type UploadStatus = "queued" | "uploading" | "done" | "failed";
type UploadItem = {
  id: string;
  file: RcFile;
  name: string;
  status: UploadStatus;
  progress: number;
  attempts: number;
  error?: string;
};

const MAX_UPLOAD_CONCURRENCY = 5;
const MAX_UPLOAD_ATTEMPTS = 3;

function getBrowserFile(file: GalleryUploadFile): RcFile {
  return "originFileObj" in file && file.originFileObj ? file.originFileObj : (file as RcFile);
}

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
  const [uploadItems, setUploadItems] = useState<UploadItem[]>([]);
  const uploadItemsRef = useRef<UploadItem[]>([]);
  const queueRef = useRef<UploadItem[]>([]);
  const activeUploadsRef = useRef(0);
  const galleryQuery = useQuery({
    queryKey: ["gallery", galleryId],
    queryFn: () => getGallery(galleryId!),
    enabled: Boolean(galleryId)
  });
  const deleteMutation = useMutation({
    mutationFn: (photoId: string) => deleteGalleryPhoto(galleryId!, photoId),
    onSuccess: async () => {
      message.success("Photo deleted");
      await queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
    }
  });
  const overallProgress = useMemo(() => {
    if (!uploadItems.length) {
      return 0;
    }
    return Math.round(
      uploadItems.reduce((total, item) => total + item.progress, 0) / uploadItems.length
    );
  }, [uploadItems]);
  const activeBatch = uploadItems.some((item) => item.status === "queued" || item.status === "uploading");

  function patchUploadItem(id: string, patch: Partial<UploadItem>) {
    uploadItemsRef.current = uploadItemsRef.current.map((item) =>
      item.id === id ? { ...item, ...patch } : item
    );
    setUploadItems(uploadItemsRef.current);
  }

  async function uploadWithRetries(item: UploadItem) {
    for (let attempt = 1; attempt <= MAX_UPLOAD_ATTEMPTS; attempt += 1) {
      try {
        patchUploadItem(item.id, {
          status: "uploading",
          attempts: attempt,
          error: undefined,
          progress: Math.max(item.progress, 5)
        });
        const objectUrl = URL.createObjectURL(item.file);
        const dimensions = await getImageDimensions(objectUrl);
        URL.revokeObjectURL(objectUrl);
        patchUploadItem(item.id, { progress: 15 });
        await uploadGalleryPhoto(
          galleryId!,
          item.file,
          {
            image_width: dimensions.width,
            image_height: dimensions.height
          },
          {
            onUploadProgress: (event) => {
              if (!event.total) {
                return;
              }
              const uploadPercent = Math.round((event.loaded / event.total) * 80);
              patchUploadItem(item.id, { progress: Math.min(95, 15 + uploadPercent) });
            }
          }
        );
        patchUploadItem(item.id, { status: "done", progress: 100 });
        return true;
      } catch (error) {
        const messageText = error instanceof Error ? error.message : "Upload failed";
        if (attempt === MAX_UPLOAD_ATTEMPTS) {
          patchUploadItem(item.id, {
            status: "failed",
            progress: 100,
            error: messageText,
            attempts: attempt
          });
          return false;
        }
        patchUploadItem(item.id, {
          status: "queued",
          progress: 0,
          error: `${messageText}. Retrying...`,
          attempts: attempt
        });
      }
    }
    return false;
  }

  function drainUploadQueue() {
    while (activeUploadsRef.current < MAX_UPLOAD_CONCURRENCY && queueRef.current.length > 0) {
      const nextItem = queueRef.current.shift()!;
      activeUploadsRef.current += 1;
      void uploadWithRetries(nextItem).finally(() => {
        activeUploadsRef.current -= 1;
        if (queueRef.current.length > 0) {
          drainUploadQueue();
          return;
        }
        if (activeUploadsRef.current === 0) {
          void queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
          const failedCount = uploadItemsRef.current.filter((item) => item.status === "failed").length;
          if (failedCount > 0) {
            message.error(`${failedCount} photo${failedCount === 1 ? "" : "s"} failed to upload`);
          } else {
            message.success("Photos uploaded");
          }
        }
      });
    }
  }

  function enqueueUpload(uploadFile: GalleryUploadFile) {
    if (!galleryId) {
      return;
    }
    const file = getBrowserFile(uploadFile);
    const id = `${file.uid}-${file.lastModified}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const item: UploadItem = {
      id,
      file,
      name: file.name,
      status: "queued",
      progress: 0,
      attempts: 0
    };
    queueRef.current.push(item);
    uploadItemsRef.current = [item, ...uploadItemsRef.current];
    setUploadItems(uploadItemsRef.current);
    drainUploadQueue();
  }

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
          enqueueUpload(file as GalleryUploadFile);
          onSuccess?.("ok");
        }}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Drop photos here or click to upload</p>
      </Upload.Dragger>

      {uploadItems.length > 0 && (
        <Space direction="vertical" size={8} style={{ width: "100%" }}>
          <Typography.Text strong>
            Upload progress: {uploadItems.filter((item) => item.status === "done").length} /{" "}
            {uploadItems.length}
          </Typography.Text>
          <Progress percent={overallProgress} status={activeBatch ? "active" : "normal"} />
          <Table
            size="small"
            rowKey="id"
            pagination={{ pageSize: 10 }}
            dataSource={uploadItems}
            columns={[
              { title: "File", dataIndex: "name" },
              {
                title: "Status",
                dataIndex: "status",
                width: 130,
                render: (status: UploadStatus) => {
                  const color = status === "done" ? "green" : status === "failed" ? "red" : "blue";
                  return <Tag color={color}>{status}</Tag>;
                }
              },
              {
                title: "Attempts",
                dataIndex: "attempts",
                width: 110
              },
              {
                title: "Progress",
                dataIndex: "progress",
                width: 220,
                render: (value: number, item) => (
                  <Progress
                    percent={value}
                    size="small"
                    status={item.status === "failed" ? "exception" : undefined}
                  />
                )
              },
              { title: "Error", dataIndex: "error" }
            ]}
          />
        </Space>
      )}

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
