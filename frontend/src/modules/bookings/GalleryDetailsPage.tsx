import { CopyOutlined, LinkOutlined, ShareAltOutlined, UploadOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  App,
  Button,
  Descriptions,
  Empty,
  Image,
  InputNumber,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  DatePicker,
} from "antd";
import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import {
  createUpgradeRequest,
  getGallery,
  reopenSelection,
  revokeGalleryAccessTokens,
  rotateGalleryAccessToken,
  updateGallery,
} from "../../api/galleries";
import dayjs from "dayjs";
import { Modal, Form, Input } from "antd";
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
  const settingsMutation = useMutation({
    mutationFn: (payload: any) => updateGallery(galleryId!, payload),
    onSuccess: async () => {
      message.success("Gallery updated");
      await queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
      await queryClient.invalidateQueries({ queryKey: ["galleries"] });
    }
  });
  const reopenMutation = useMutation({
    mutationFn: () => reopenSelection(galleryId!),
    onSuccess: async () => {
      message.success("Gallery selection reopened");
      await queryClient.invalidateQueries({ queryKey: ["gallery", galleryId] });
      await queryClient.invalidateQueries({ queryKey: ["galleries"] });
    }
  });
  const gallery = galleryQuery.data;
  const [upgradeModalVisible, setUpgradeModalVisible] = useState(false);
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [publicGalleryUrl, setPublicGalleryUrl] = useState("");
  const [upgradeForm] = Form.useForm();
  const [shareForm] = Form.useForm<{
    password?: string;
    expires_at?: dayjs.Dayjs | null;
  }>();
  const rotateTokenMutation = useMutation({
    mutationFn: () => rotateGalleryAccessToken(galleryId!),
    onSuccess: (data) => {
      const nextUrl = data.access_url ? `${window.location.origin}${data.access_url}` : "";
      setPublicGalleryUrl(nextUrl);
      message.success("Gallery link rotated");
    }
  });
  const revokeTokenMutation = useMutation({
    mutationFn: () => revokeGalleryAccessTokens(galleryId!),
    onSuccess: () => {
      setPublicGalleryUrl("");
      message.success("Gallery link revoked");
    }
  });

  useEffect(() => {
    if (gallery && shareModalVisible) {
      shareForm.setFieldsValue({
        password: "",
        expires_at: gallery.expires_at ? dayjs(gallery.expires_at) : null
      });
    }
  }, [gallery, shareForm, shareModalVisible]);

  const copyPublicLink = async () => {
    if (!publicGalleryUrl) {
      message.error("Rotate the gallery link first");
      return;
    }
    try {
      await navigator.clipboard.writeText(publicGalleryUrl);
      message.success("Gallery link copied");
    } catch {
      message.error("Unable to copy link");
    }
  };

  const saveShareSettings = async () => {
    const values = await shareForm.validateFields();
    await settingsMutation.mutateAsync({
      password: values.password?.trim() ? values.password.trim() : undefined,
      expires_at: values.expires_at ? values.expires_at.toISOString() : null
    });
    setShareModalVisible(false);
  };

  const clearGalleryPassword = async () => {
    await settingsMutation.mutateAsync({ password: null });
    shareForm.setFieldValue("password", "");
    message.success("Gallery password cleared");
  };

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
          <Button
            aria-label="Share gallery"
            icon={<ShareAltOutlined />}
            onClick={() => setShareModalVisible(true)}
          >
            Share
          </Button>
          <Button
            icon={<LinkOutlined />}
            disabled={!publicGalleryUrl}
            onClick={() => {
              if (publicGalleryUrl) {
                window.open(publicGalleryUrl, "_blank", "noopener,noreferrer");
              }
            }}
          >
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
            <Descriptions.Item label="Selection Limit">
              <InputNumber
                value={gallery.selection_limit}
                min={0}
                onChange={(value) => settingsMutation.mutate({ selection_limit: value })}
              />
            </Descriptions.Item>
            <Descriptions.Item label="Allow Download">
              <Switch
                checked={gallery.allow_download}
                onChange={(checked) => settingsMutation.mutate({ allow_download: checked })}
              />
            </Descriptions.Item>
            <Descriptions.Item label="Watermark">
              <Switch
                checked={gallery.allow_watermark}
                onChange={(checked) => settingsMutation.mutate({ allow_watermark: checked })}
              />
            </Descriptions.Item>
            <Descriptions.Item label="Selection Deadline">
              <DatePicker
                showTime
                value={gallery?.selection_deadline ? dayjs(gallery.selection_deadline) : undefined}
                onChange={(value) =>
                  settingsMutation.mutate({ selection_deadline: value ? value.toISOString() : null })
                }
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
          <div style={{ marginTop: 16 }}>
            <Button type="default" onClick={() => setUpgradeModalVisible(true)}>
              Request Upgrade
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={() => reopenMutation.mutate()}>
              Reopen Selection
            </Button>
            <Modal
              title="Request Upgrade"
              open={upgradeModalVisible}
              onCancel={() => setUpgradeModalVisible(false)}
              onOk={async () => {
                try {
                  const values = await upgradeForm.validateFields();
                  await createUpgradeRequest(galleryId!, {
                    requested_limit: values.requested_limit,
                    additional_photos: values.additional_photos,
                    price_per_photo: values.price_per_photo,
                    notes: values.notes,
                  });
                  message.success("Upgrade request created");
                  setUpgradeModalVisible(false);
                } catch (err: any) {
                  message.error(err?.response?.data?.message ?? "Failed to create upgrade request");
                }
              }}
            >
              <Form form={upgradeForm} layout="vertical">
                <Form.Item name="requested_limit" label="Requested Limit" rules={[{ required: true }] }>
                  <InputNumber min={1} />
                </Form.Item>
                <Form.Item name="additional_photos" label="Additional Photos" rules={[{ required: true }] }>
                  <InputNumber min={0} />
                </Form.Item>
                <Form.Item name="price_per_photo" label="Price per Photo" rules={[{ required: true }] }>
                  <InputNumber min={0} step={0.01} />
                </Form.Item>
                <Form.Item name="notes" label="Notes">
                  <Input.TextArea />
                </Form.Item>
              </Form>
            </Modal>
          </div>
          <Modal
            title="Share Gallery"
            open={shareModalVisible}
            onCancel={() => setShareModalVisible(false)}
            onOk={saveShareSettings}
            okText="Save Sharing Settings"
            confirmLoading={settingsMutation.isPending}
          >
            <Space direction="vertical" size={16} className="full-width-control">
              <Typography.Text type="secondary">
                Share this client gallery link after opening selection. Password is optional and write-only.
              </Typography.Text>
              <Input
                readOnly
                value={publicGalleryUrl}
                addonAfter={
                  <Button
                    type="text"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={copyPublicLink}
                    aria-label="Copy gallery link"
                  />
                }
              />
              <Form form={shareForm} layout="vertical" requiredMark={false}>
                <Form.Item
                  name="password"
                  label="Gallery Password"
                  extra="Leave blank to keep the current password. Use Clear Password to remove it."
                >
                  <Input.Password autoComplete="new-password" placeholder="Set a client access password" />
                </Form.Item>
                <Form.Item name="expires_at" label="Link Expiry">
                  <DatePicker showTime className="full-width-control" />
                </Form.Item>
              </Form>
              <Space wrap>
                <Button
                  aria-label="Copy Link"
                  onClick={copyPublicLink}
                  icon={<CopyOutlined />}
                >
                  Copy Link
                </Button>
                <Button
                  onClick={() => rotateTokenMutation.mutate()}
                  loading={rotateTokenMutation.isPending}
                >
                  Rotate Link
                </Button>
                <Button
                  danger
                  onClick={() => revokeTokenMutation.mutate()}
                  loading={revokeTokenMutation.isPending}
                >
                  Revoke Link
                </Button>
                <Button onClick={() => statusMutation.mutate("SELECTION_OPEN")}>
                  Open Selection
                </Button>
                <Button danger onClick={clearGalleryPassword} loading={settingsMutation.isPending}>
                  Clear Password
                </Button>
              </Space>
            </Space>
          </Modal>
        </>
      ) : null}
    </Space>
  );
}
