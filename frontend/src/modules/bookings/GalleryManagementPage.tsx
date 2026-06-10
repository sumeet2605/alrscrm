import { EyeOutlined, PlusOutlined, UploadOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
  App
} from "antd";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { listBookings } from "../../api/bookings";
import { createGallery, getGalleryMetrics, listGalleries } from "../../api/galleries";
import { useAuth } from "../../contexts/AuthContext";
import type { GalleryPayload } from "../../types/galleries";
import {
  canManageGalleries,
  canUploadGalleryPhotos,
  galleryStatusColor,
  galleryStatuses,
  labelFromEnum
} from "./galleryOptions";

export function GalleryManagementPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [isOpen, setIsOpen] = useState(false);
  const [form] = Form.useForm<GalleryPayload>();
  const galleriesQuery = useQuery({
    queryKey: ["galleries"],
    queryFn: () => listGalleries({ page: 1, page_size: 50 })
  });
  const metricsQuery = useQuery({ queryKey: ["gallery-metrics"], queryFn: getGalleryMetrics });
  const bookingsQuery = useQuery({
    queryKey: ["bookings", "gallery-options"],
    queryFn: () => listBookings({ page: 1, page_size: 100 })
  });
  const bookingOptions = useMemo(
    () =>
      (bookingsQuery.data?.items ?? []).flatMap((booking) =>
        booking.items.map((item) => ({
          value: `${booking.id}:${item.id}`,
          label: `${booking.booking_number} · ${booking.family?.primary_contact_name ?? "Family"} · ${labelFromEnum(item.service_type)}`
        }))
      ),
    [bookingsQuery.data?.items]
  );
  const createMutation = useMutation({
    mutationFn: (values: GalleryPayload) => createGallery(values),
    onSuccess: async (gallery) => {
      message.success("Gallery created");
      setIsOpen(false);
      form.resetFields();
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["galleries"] }),
        queryClient.invalidateQueries({ queryKey: ["gallery-metrics"] })
      ]);
      navigate(`/galleries/${gallery.id}`);
    }
  });

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Galleries</Typography.Title>
          <Typography.Text type="secondary">
            Manage uploaded photo galleries and client selections.
          </Typography.Text>
        </div>
        {canManageGalleries(roleNames) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsOpen(true)}>
            New Gallery
          </Button>
        )}
      </div>

      <div className="metric-grid">
        <Statistic title="Total Galleries" value={metricsQuery.data?.total_galleries ?? 0} />
        <Statistic title="Photos Uploaded" value={metricsQuery.data?.photos_uploaded ?? 0} />
        <Statistic
          title="Selection Open"
          value={metricsQuery.data?.selection_open_galleries ?? 0}
        />
        <Statistic title="Favorites" value={metricsQuery.data?.favorite_count ?? 0} />
      </div>

      <Table
        rowKey="id"
        dataSource={galleriesQuery.data?.items ?? []}
        loading={galleriesQuery.isLoading}
        columns={[
          { title: "Gallery Name", dataIndex: "gallery_name" },
          { title: "Booking Number", dataIndex: "booking_number" },
          { title: "Family", dataIndex: "family_name" },
          {
            title: "Status",
            dataIndex: "gallery_status",
            render: (value) => <Tag color={galleryStatusColor(value)}>{labelFromEnum(value)}</Tag>
          },
          { title: "Photo Count", dataIndex: "photo_count" },
          { title: "Favorites", dataIndex: "favorite_count" },
          {
            title: "Actions",
            render: (_, gallery) => (
              <Space>
                <Button icon={<EyeOutlined />} onClick={() => navigate(`/galleries/${gallery.id}`)} />
                {canUploadGalleryPhotos(roleNames) && (
                  <Button
                    icon={<UploadOutlined />}
                    onClick={() => navigate(`/galleries/${gallery.id}/upload`)}
                  />
                )}
              </Space>
            )
          }
        ]}
      />

      <Modal
        title="Create Gallery"
        open={isOpen}
        onCancel={() => setIsOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={createMutation.isPending}
      >
        <Form
          form={form}
          layout="vertical"
          requiredMark={false}
          initialValues={{ gallery_status: "DRAFT" }}
          onFinish={(values) => createMutation.mutate(values)}
        >
          <Form.Item
            label="Booking Item"
            name="booking_item_id"
            rules={[{ required: true, message: "Booking item is required" }]}
          >
            <Select
              loading={bookingsQuery.isLoading}
              options={bookingOptions}
              onChange={(value) => {
                const [bookingId, bookingItemId] = String(value).split(":");
                form.setFieldsValue({ booking_id: bookingId, booking_item_id: bookingItemId });
              }}
            />
          </Form.Item>
          <Form.Item name="booking_id" hidden>
            <Input />
          </Form.Item>
          <Form.Item label="Gallery Name" name="gallery_name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Status" name="gallery_status">
            <Select
              options={galleryStatuses.map((status) => ({
                value: status,
                label: labelFromEnum(status)
              }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
