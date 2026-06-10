import { DownloadOutlined, ReloadOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Alert, Button, Card, Descriptions, Space, Tag, Typography, message } from "antd";
import { useParams } from "react-router-dom";

import {
  downloadClientDelivery,
  getClientDelivery,
  requestDeliveryReopen
} from "../../api/delivery";
import { deliveryStatusColor, labelFromEnum, zipStatusColor } from "./deliveryOptions";

export function ClientDeliveryPage() {
  const { deliveryId } = useParams();
  const queryClient = useQueryClient();
  const deliveryQuery = useQuery({
    queryKey: ["client-delivery", deliveryId],
    queryFn: () => getClientDelivery(deliveryId!),
    enabled: Boolean(deliveryId),
    retry: false
  });
  const delivery = deliveryQuery.data;

  const downloadMutation = useMutation({
    mutationFn: () => downloadClientDelivery(deliveryId!),
    onSuccess: async () => {
      message.success("Download recorded");
      await queryClient.invalidateQueries({ queryKey: ["client-delivery", deliveryId] });
    },
    onError: () => message.error("Download is not available")
  });

  const reopenMutation = useMutation({
    mutationFn: () => requestDeliveryReopen(deliveryId!, "Client requested re-download"),
    onSuccess: async () => {
      message.success("Reopen request submitted");
      await queryClient.invalidateQueries({ queryKey: ["client-delivery", deliveryId] });
    },
    onError: () => message.error("Unable to request reopen")
  });

  const canDownload =
    delivery &&
    ["READY", "SENT", "DELIVERED", "REOPENED"].includes(delivery.delivery_status) &&
    delivery.remaining_downloads > 0;

  return (
    <main className="client-selection-shell">
      <Space direction="vertical" size={20} className="client-selection-panel">
        <div>
          <Typography.Title level={2}>Your Delivery</Typography.Title>
          <Typography.Text type="secondary">
            Download your edited gallery before the delivery expires.
          </Typography.Text>
        </div>

        {deliveryQuery.isError ? (
          <Alert
            type="error"
            showIcon
            message="Delivery is not available"
            description="The link may be expired, closed, or not ready yet."
          />
        ) : null}

        {delivery ? (
          <Card>
            <Space direction="vertical" size={16} className="page-stack">
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="Delivery">
                  {delivery.delivery_number}
                </Descriptions.Item>
                <Descriptions.Item label="Status">
                  <Tag color={deliveryStatusColor(delivery.delivery_status)}>
                    {labelFromEnum(delivery.delivery_status)}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="ZIP">
                  <Tag color={zipStatusColor(delivery.zip_generation_status)}>
                    {labelFromEnum(delivery.zip_generation_status)}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Gallery">{delivery.gallery_name}</Descriptions.Item>
                <Descriptions.Item label="Booking">{delivery.booking_number}</Descriptions.Item>
                <Descriptions.Item label="Edited Photos">
                  {delivery.edited_photo_count}
                </Descriptions.Item>
                <Descriptions.Item label="Downloads Remaining">
                  {delivery.remaining_downloads}
                </Descriptions.Item>
                <Descriptions.Item label="Expiry Date">{delivery.expiry_date}</Descriptions.Item>
              </Descriptions>
              <Space wrap>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  disabled={!canDownload}
                  loading={downloadMutation.isPending}
                  onClick={() => downloadMutation.mutate()}
                >
                  Download
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  disabled={delivery.delivery_status === "REOPEN_REQUESTED"}
                  loading={reopenMutation.isPending}
                  onClick={() => reopenMutation.mutate()}
                >
                  Request Reopen
                </Button>
              </Space>
            </Space>
          </Card>
        ) : null}
      </Space>
    </main>
  );
}
