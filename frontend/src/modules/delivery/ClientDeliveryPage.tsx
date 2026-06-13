import { DownloadOutlined, LockOutlined, ReloadOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  Descriptions,
  Form,
  Input,
  Modal,
  Space,
  Tag,
  Typography,
  message
} from "antd";
import axios from "axios";
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import {
  authenticateClientDelivery,
  downloadClientDelivery,
  getClientDelivery,
  requestDeliveryReopen
} from "../../api/delivery";
import type { DeliveryReopenPayload } from "../../types/delivery";
import { deliveryStatusColor, labelFromEnum, zipStatusColor } from "./deliveryOptions";

function responseStatus(error: unknown): number | undefined {
  if (!axios.isAxiosError(error)) {
    return undefined;
  }
  return error.response?.status;
}

export function ClientDeliveryPage() {
  const { token } = useParams();
  const queryClient = useQueryClient();
  const [password, setPassword] = useState("");
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [reopenOpen, setReopenOpen] = useState(false);
  const [reopenForm] = Form.useForm<DeliveryReopenPayload>();

  const deliveryQuery = useQuery({
    queryKey: ["client-delivery", token],
    queryFn: () => getClientDelivery(token!),
    enabled: Boolean(token),
    retry: false
  });
  const delivery = deliveryQuery.data;

  const authenticateMutation = useMutation({
    mutationFn: () => authenticateClientDelivery(token!, password || undefined),
    onSuccess: (data) => {
      setSessionToken(data.session_token);
      message.success("Delivery access verified");
    },
    onError: () => message.error("Unable to verify delivery access")
  });

  const downloadMutation = useMutation({
    mutationFn: async () => {
      let activeSession = sessionToken;
      if (!activeSession) {
        const auth = await authenticateClientDelivery(token!, password || undefined);
        activeSession = auth.session_token;
        setSessionToken(activeSession);
      }
      return downloadClientDelivery(token!, activeSession);
    },
    onSuccess: async (data) => {
      message.success("Secure download link generated");
      window.open(data.download_url, "_blank", "noopener,noreferrer");
      await queryClient.invalidateQueries({ queryKey: ["client-delivery", token] });
    },
    onError: () => message.error("Download is not available")
  });

  const reopenMutation = useMutation({
    mutationFn: (payload: DeliveryReopenPayload) => requestDeliveryReopen(token!, payload),
    onSuccess: async () => {
      message.success("Reopen request submitted");
      setReopenOpen(false);
      reopenForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["client-delivery", token] });
    },
    onError: () => message.error("Unable to request reopen")
  });

  const errorStatus = responseStatus(deliveryQuery.error);
  const canDownload = useMemo(
    () =>
      delivery &&
      ["READY", "SENT", "DELIVERED", "REOPENED"].includes(delivery.delivery_status) &&
      delivery.remaining_downloads > 0,
    [delivery]
  );

  return (
    <main className="client-selection-shell">
      <Space direction="vertical" size={20} className="client-selection-panel">
        <div>
          <Typography.Title level={2}>Your Delivery</Typography.Title>
          <Typography.Text type="secondary">
            Download your edited gallery before the delivery expires.
          </Typography.Text>
        </div>

        {deliveryQuery.isError && errorStatus === 401 ? (
          <Alert
            type="error"
            showIcon
            message="Invalid delivery link"
            description="This secure delivery link is invalid or has been revoked."
          />
        ) : null}
        {deliveryQuery.isError && errorStatus === 410 ? (
          <Alert
            type="warning"
            showIcon
            message="Delivery expired"
            description="This delivery has expired. Contact the studio if you need access again."
          />
        ) : null}
        {deliveryQuery.isError && ![401, 410].includes(errorStatus ?? 0) ? (
          <Alert
            type="error"
            showIcon
            message="Delivery is not available"
            description="The link may be closed, not ready yet, or temporarily unavailable."
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
                <Descriptions.Item label="Downloads">
                  {delivery.download_count}/{delivery.max_downloads}
                </Descriptions.Item>
                <Descriptions.Item label="Downloads Remaining">
                  {delivery.remaining_downloads}
                </Descriptions.Item>
                <Descriptions.Item label="Expiry Date">{delivery.expiry_date}</Descriptions.Item>
              </Descriptions>

              {delivery.password_required && !sessionToken ? (
                <Space.Compact className="full-width">
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Delivery password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    onPressEnter={() => authenticateMutation.mutate()}
                  />
                  <Button
                    type="primary"
                    loading={authenticateMutation.isPending}
                    onClick={() => authenticateMutation.mutate()}
                  >
                    Unlock
                  </Button>
                </Space.Compact>
              ) : null}

              <Space wrap>
                <Button
                  type="primary"
                  icon={<DownloadOutlined />}
                  disabled={!canDownload || (delivery.password_required && !sessionToken)}
                  loading={downloadMutation.isPending}
                  onClick={() => downloadMutation.mutate()}
                >
                  Download Artifact
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  disabled={delivery.delivery_status !== "DELIVERED"}
                  loading={reopenMutation.isPending}
                  onClick={() => setReopenOpen(true)}
                >
                  Request Reopen
                </Button>
              </Space>
            </Space>
          </Card>
        ) : null}
      </Space>

      <Modal
        title="Request Delivery Reopen"
        open={reopenOpen}
        okText="Submit Request"
        confirmLoading={reopenMutation.isPending}
        onCancel={() => setReopenOpen(false)}
        onOk={() => reopenForm.submit()}
      >
        <Form
          form={reopenForm}
          layout="vertical"
          onFinish={(values) => reopenMutation.mutate(values)}
        >
          <Form.Item
            name="requested_by_name"
            label="Name"
            rules={[{ required: true, message: "Name is required" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="requested_by_email"
            label="Email"
            rules={[
              { required: true, message: "Email is required" },
              { type: "email", message: "Enter a valid email" }
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="reason"
            label="Reason"
            rules={[{ required: true, message: "Reason is required" }]}
          >
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </main>
  );
}
