import {
  DownloadOutlined,
  KeyOutlined,
  LinkOutlined,
  ReloadOutlined,
  SendOutlined,
  StopOutlined,
  ToolOutlined
} from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Row,
  Space,
  Table,
  Tag,
  Typography,
  message
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { useParams } from "react-router-dom";

import {
  approveDeliveryReopen,
  closeDelivery,
  generateDeliveryZip,
  getDeliveryJob,
  listDeliveryDownloads,
  rotateDeliveryAccessToken,
  revokeDeliveryAccessTokens,
  sendDelivery
} from "../../api/delivery";
import { useAuth } from "../../contexts/AuthContext";
import type { DeliveryArtifact, DeliveryDownload } from "../../types/delivery";
import {
  canManageDelivery,
  deliveryStatusColor,
  labelFromEnum,
  zipStatusColor
} from "./deliveryOptions";

export function DeliveryDetailPage() {
  const { deliveryId } = useParams();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const canManage = canManageDelivery(roleNames);
  const jobQuery = useQuery({
    queryKey: ["delivery-job", deliveryId],
    queryFn: () => getDeliveryJob(deliveryId!),
    enabled: Boolean(deliveryId)
  });
  const downloadsQuery = useQuery({
    queryKey: ["delivery-downloads", deliveryId],
    queryFn: () => listDeliveryDownloads(deliveryId!),
    enabled: Boolean(deliveryId)
  });
  const job = jobQuery.data;

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["delivery-job", deliveryId] });
    await queryClient.invalidateQueries({ queryKey: ["delivery-downloads", deliveryId] });
    await queryClient.invalidateQueries({ queryKey: ["delivery-jobs"] });
    await queryClient.invalidateQueries({ queryKey: ["delivery-metrics"] });
  };

  const generateMutation = useMutation({
    mutationFn: generateDeliveryZip,
    onSuccess: async () => {
      message.success("Delivery ZIP generated");
      await refresh();
    }
  });
  const sendMutation = useMutation({
    mutationFn: sendDelivery,
    onSuccess: async () => {
      message.success("Delivery sent");
      await refresh();
    }
  });
  const reopenMutation = useMutation({
    mutationFn: approveDeliveryReopen,
    onSuccess: async () => {
      message.success("Delivery reopened");
      await refresh();
    }
  });
  const closeMutation = useMutation({
    mutationFn: closeDelivery,
    onSuccess: async () => {
      message.success("Delivery closed");
      await refresh();
    }
  });
  const rotateTokenMutation = useMutation({
    mutationFn: rotateDeliveryAccessToken,
    onSuccess: async () => {
      message.success("Delivery link rotated");
      await refresh();
    }
  });
  const revokeTokenMutation = useMutation({
    mutationFn: revokeDeliveryAccessTokens,
    onSuccess: async () => {
      message.success("Delivery links revoked");
      await refresh();
    }
  });

  const clientLink = job?.delivery_access_url
    ? `${window.location.origin}${job.delivery_access_url}`
    : null;
  const downloadColumns: ColumnsType<DeliveryDownload> = [
    { title: "Downloaded At", dataIndex: "downloaded_at" },
    { title: "IP Address", dataIndex: "ip_address" },
    { title: "User Agent", dataIndex: "user_agent" }
  ];
  const artifactColumns: ColumnsType<DeliveryArtifact> = [
    { title: "Type", dataIndex: "artifact_type" },
    { title: "Size", dataIndex: "file_size", render: (value: number) => `${value} bytes` },
    { title: "Generated At", dataIndex: "generated_at" },
    { title: "Checksum", dataIndex: "checksum", ellipsis: true }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{job?.delivery_number ?? "Delivery"}</Typography.Title>
          <Typography.Text type="secondary">
            Manage final client delivery, download limits, expiry, and reopen requests.
          </Typography.Text>
        </div>
        {canManage ? (
          <Space wrap>
            <Button
              icon={<ToolOutlined />}
              onClick={() => job && generateMutation.mutate(job.id)}
              disabled={
                !job || !["PENDING", "ZIP_GENERATING", "REOPENED"].includes(job.delivery_status)
              }
            >
              Generate ZIP
            </Button>
            <Button
              icon={<SendOutlined />}
              type="primary"
              onClick={() => job && sendMutation.mutate(job.id)}
              disabled={!job || !["READY", "REOPENED"].includes(job.delivery_status)}
            >
              Send
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => job && reopenMutation.mutate(job.id)}
              disabled={job?.delivery_status !== "REOPEN_REQUESTED"}
            >
              Approve Reopen
            </Button>
            <Button
              icon={<KeyOutlined />}
              onClick={() => job && rotateTokenMutation.mutate(job.id)}
              disabled={!job || job.delivery_status === "CLOSED"}
            >
              Rotate Link
            </Button>
            <Button
              icon={<StopOutlined />}
              onClick={() => job && revokeTokenMutation.mutate(job.id)}
              disabled={!job || job.delivery_status === "CLOSED"}
            >
              Revoke Links
            </Button>
            <Button
              danger
              onClick={() => job && closeMutation.mutate(job.id)}
              disabled={!job || !["DELIVERED", "EXPIRED", "REOPENED"].includes(job.delivery_status)}
            >
              Close
            </Button>
          </Space>
        ) : null}
      </div>

      {jobQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load delivery"
          description="Refresh the page or try again after checking your connection."
        />
      ) : null}

      {job ? (
        <Row gutter={[16, 16]}>
          <Col xs={24} xl={16}>
            <Card title="Delivery Details" loading={jobQuery.isLoading}>
              <Descriptions column={{ xs: 1, md: 2 }} bordered size="small">
                <Descriptions.Item label="Status">
                  <Tag color={deliveryStatusColor(job.delivery_status)}>
                    {labelFromEnum(job.delivery_status)}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="ZIP">
                  <Tag color={zipStatusColor(job.zip_generation_status)}>
                    {labelFromEnum(job.zip_generation_status)}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Family">{job.family_name}</Descriptions.Item>
                <Descriptions.Item label="Booking">{job.booking_number}</Descriptions.Item>
                <Descriptions.Item label="Gallery">{job.gallery_name}</Descriptions.Item>
                <Descriptions.Item label="Service">
                  {labelFromEnum(job.service_type)}
                </Descriptions.Item>
                <Descriptions.Item label="Edited Photos">
                  {job.edited_photo_count}
                </Descriptions.Item>
                <Descriptions.Item label="Downloads">
                  {job.download_count}/{job.max_downloads}
                </Descriptions.Item>
                <Descriptions.Item label="Delivery Date">{job.delivery_date}</Descriptions.Item>
                <Descriptions.Item label="Expiry Date">{job.expiry_date}</Descriptions.Item>
                <Descriptions.Item label="Client Link" span={2}>
                  {clientLink ? (
                    <Space>
                      <Typography.Text copyable>{clientLink}</Typography.Text>
                      <Button icon={<LinkOutlined />} href={clientLink} target="_blank" />
                    </Space>
                  ) : (
                    <Typography.Text type="secondary">
                      Secure link is shown only after send or rotation.
                    </Typography.Text>
                  )}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
          <Col xs={24} xl={8}>
            <Card title="Policy">
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="Allow Re-download">
                  {job.allow_re_download ? "Yes" : "No"}
                </Descriptions.Item>
                <Descriptions.Item label="Re-download Fee">
                  ₹{job.re_download_fee}
                </Descriptions.Item>
                <Descriptions.Item label="Watermark">
                  {job.watermark_enabled ? "Enabled" : "Disabled"}
                </Descriptions.Item>
                <Descriptions.Item label="Original Download">
                  {job.original_download_enabled ? "Enabled" : "Disabled"}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
        </Row>
      ) : null}

      <Card title="Download Audit" extra={<DownloadOutlined />}>
        <Table<DeliveryDownload>
          rowKey="id"
          dataSource={downloadsQuery.data ?? []}
          loading={downloadsQuery.isLoading}
          columns={downloadColumns}
        />
      </Card>

      <Card title="Delivery Artifacts">
        <Table<DeliveryArtifact>
          rowKey="id"
          dataSource={job?.artifacts ?? []}
          loading={jobQuery.isLoading}
          columns={artifactColumns}
        />
      </Card>
    </Space>
  );
}
