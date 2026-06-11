import { EyeOutlined, FilterOutlined, SendOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Alert, Button, Input, Select, Space, Table, Tag, Typography, message } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  approveDeliveryReopen,
  generateDeliveryZip,
  listDeliveryJobs,
  sendDelivery
} from "../../api/delivery";
import { useAuth } from "../../contexts/AuthContext";
import type { DeliveryJob, DeliveryStatus } from "../../types/delivery";
import {
  canManageDelivery,
  deliveryStatusColor,
  deliveryStatuses,
  labelFromEnum,
  zipStatusColor
} from "./deliveryOptions";

export function DeliveryQueuePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const canManage = canManageDelivery(roleNames);
  const [status, setStatus] = useState<DeliveryStatus | undefined>();
  const [search, setSearch] = useState("");
  const jobsQuery = useQuery({
    queryKey: ["delivery-jobs", status, search],
    queryFn: () =>
      listDeliveryJobs({
        page: 1,
        page_size: 50,
        status,
        search: search || undefined
      })
  });

  const refresh = async () => {
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

  const columns: ColumnsType<DeliveryJob> = [
    {
      title: "Delivery",
      dataIndex: "delivery_number",
      render: (value: string, job) => (
        <Button type="link" onClick={() => navigate(`/delivery/${job.id}`)}>
          {value}
        </Button>
      )
    },
    { title: "Gallery", dataIndex: "gallery_name" },
    { title: "Booking", dataIndex: "booking_number" },
    { title: "Family", dataIndex: "family_name" },
    { title: "Service", dataIndex: "service_type", render: (value: string) => labelFromEnum(value) },
    {
      title: "Status",
      dataIndex: "delivery_status",
      render: (value: DeliveryStatus) => (
        <Tag color={deliveryStatusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    {
      title: "ZIP",
      dataIndex: "zip_generation_status",
      render: (value: DeliveryJob["zip_generation_status"]) => (
        <Tag color={zipStatusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    { title: "Downloads", render: (_, job) => `${job.download_count}/${job.max_downloads}` },
    { title: "Expiry", dataIndex: "expiry_date" },
    {
      title: "Actions",
      width: 220,
      render: (_, job) => (
        <Space>
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/delivery/${job.id}`)} />
          {canManage ? (
            <>
              <Button
                onClick={() => generateMutation.mutate(job.id)}
                disabled={!["PENDING", "ZIP_GENERATING", "REOPENED"].includes(job.delivery_status)}
              >
                ZIP
              </Button>
              <Button
                icon={<SendOutlined />}
                onClick={() => sendMutation.mutate(job.id)}
                disabled={!["READY", "REOPENED"].includes(job.delivery_status)}
              />
              <Button
                onClick={() => reopenMutation.mutate(job.id)}
                disabled={job.delivery_status !== "REOPEN_REQUESTED"}
              >
                Reopen
              </Button>
            </>
          ) : null}
        </Space>
      )
    }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Delivery Queue</Typography.Title>
          <Typography.Text type="secondary">
            Prepare final delivery links, send client access, and manage reopen requests.
          </Typography.Text>
        </div>
      </div>

      <Space wrap>
        <FilterOutlined />
        <Select
          allowClear
          placeholder="Status"
          value={status}
          className="filter-control"
          options={deliveryStatuses.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={setStatus}
        />
        <Input.Search
          allowClear
          placeholder="Search delivery, booking, or gallery"
          className="search-control"
          onSearch={setSearch}
        />
      </Space>

      {jobsQuery.isError ? (
        <Alert
          type="error"
          showIcon
          message="Unable to load delivery queue"
          description="Refresh the page or try again after checking your connection."
        />
      ) : null}

      <Table<DeliveryJob>
        rowKey="id"
        dataSource={jobsQuery.data?.items ?? []}
        loading={jobsQuery.isLoading}
        columns={columns}
      />
    </Space>
  );
}
