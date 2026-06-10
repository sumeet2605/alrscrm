import { EyeOutlined, FilterOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Button, Select, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { listEditingJobs } from "../../api/editing";
import type { EditingJob, EditingPriority, EditingStatus } from "../../types/editing";
import {
  editingPriorities,
  editingStatusColor,
  editingStatuses,
  labelFromEnum,
  priorityColor
} from "./editingOptions";

export function EditingQueuePage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<EditingStatus | undefined>();
  const [priority, setPriority] = useState<EditingPriority | undefined>();
  const jobsQuery = useQuery({
    queryKey: ["editing-jobs", status, priority],
    queryFn: () =>
      listEditingJobs({
        page: 1,
        page_size: 50,
        status,
        priority
      })
  });

  const columns: ColumnsType<EditingJob> = [
    {
      title: "Gallery",
      dataIndex: "gallery_name",
      render: (value: string | null | undefined, job) => (
        <Button type="link" onClick={() => navigate(`/production/editing/${job.id}`)}>
          {value ?? "Editing Job"}
        </Button>
      )
    },
    { title: "Booking", dataIndex: "booking_number" },
    { title: "Family", dataIndex: "family_name" },
    { title: "Service", dataIndex: "service_type", render: (value: string) => labelFromEnum(value) },
    {
      title: "Priority",
      dataIndex: "priority",
      render: (value: EditingPriority) => <Tag color={priorityColor(value)}>{labelFromEnum(value)}</Tag>
    },
    {
      title: "Status",
      dataIndex: "editing_status",
      render: (value: EditingStatus) => (
        <Tag color={editingStatusColor(value)}>{labelFromEnum(value)}</Tag>
      )
    },
    {
      title: "Photos",
      render: (_, job) => `${job.completed_photo_count}/${job.selected_photo_count}`
    },
    { title: "Due Date", dataIndex: "due_date" },
    {
      title: "Editor",
      render: (_, job) =>
        job.assigned_editor
          ? `${job.assigned_editor.first_name} ${job.assigned_editor.last_name}`
          : "Unassigned"
    },
    {
      title: "Actions",
      width: 96,
      render: (_, job) => (
        <Button icon={<EyeOutlined />} onClick={() => navigate(`/production/editing/${job.id}`)} />
      )
    }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Editing Queue</Typography.Title>
          <Typography.Text type="secondary">
            Assign, track, review, and prepare selected galleries for delivery.
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
          options={editingStatuses.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={setStatus}
        />
        <Select
          allowClear
          placeholder="Priority"
          value={priority}
          className="filter-control"
          options={editingPriorities.map((item) => ({ value: item, label: labelFromEnum(item) }))}
          onChange={setPriority}
        />
      </Space>

      <Table<EditingJob>
        rowKey="id"
        dataSource={jobsQuery.data?.items ?? []}
        loading={jobsQuery.isLoading}
        columns={columns}
      />
    </Space>
  );
}
