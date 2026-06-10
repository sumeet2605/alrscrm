import {
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  PlusOutlined,
  SearchOutlined
} from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, DatePicker, Input, Popconfirm, Select, Space, Table, Tag, Typography, message } from "antd";
import type { TableProps } from "antd";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { deleteFamily, listFamilies } from "../../api/families";
import { listBranches } from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import type { Family, FamilyStatus, LeadSource } from "../../types/families";
import { canDeleteFamilies, canWriteFamilies, familyStatusColor, familyStatuses, labelFromEnum, leadSources } from "./familyOptions";

const { RangePicker } = DatePicker;

export function FamilyListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<FamilyStatus | undefined>();
  const [source, setSource] = useState<LeadSource | undefined>();
  const [branchId, setBranchId] = useState<string | undefined>();
  const [eddRange, setEddRange] = useState<[string, string] | undefined>();
  const debouncedSearch = useDebouncedValue(search);

  const familiesQuery = useQuery({
    queryKey: ["families", page, debouncedSearch, status, source, branchId, eddRange],
    queryFn: () =>
      listFamilies({
        page,
        page_size: 10,
        search: debouncedSearch || undefined,
        status,
        source,
        branch_id: branchId,
        edd_from: eddRange?.[0],
        edd_to: eddRange?.[1]
      })
  });

  const branchesQuery = useQuery({
    queryKey: ["branches", "family-filter"],
    queryFn: () => listBranches({ page: 1, page_size: 100 })
  });

  const deleteMutation = useMutation({
    mutationFn: deleteFamily,
    onSuccess: async () => {
      message.success("Family deleted");
      await queryClient.invalidateQueries({ queryKey: ["families"] });
    }
  });

  const columns: TableProps<Family>["columns"] = [
    {
      title: "Family Code",
      dataIndex: "family_code",
      sorter: (a, b) => a.family_code.localeCompare(b.family_code),
      render: (value, record) => <Button type="link" onClick={() => navigate(`/families/${record.id}`)}>{value}</Button>
    },
    {
      title: "Primary Contact",
      dataIndex: "primary_contact_name",
      sorter: (a, b) => a.primary_contact_name.localeCompare(b.primary_contact_name)
    },
    { title: "Partner", dataIndex: "partner_name", responsive: ["lg"], render: (value) => value || "-" },
    { title: "Phone", dataIndex: "primary_contact_phone" },
    {
      title: "EDD",
      dataIndex: "expected_delivery_date",
      responsive: ["md"],
      sorter: (a, b) => (a.expected_delivery_date ?? "").localeCompare(b.expected_delivery_date ?? ""),
      render: (value) => (value ? dayjs(value).format("DD MMM YYYY") : "-")
    },
    { title: "Source", dataIndex: "source", responsive: ["lg"], render: (value) => labelFromEnum(value) },
    {
      title: "Status",
      dataIndex: "status",
      render: (value: FamilyStatus) => <Tag color={familyStatusColor(value)}>{labelFromEnum(value)}</Tag>
    },
    {
      title: "Created",
      dataIndex: "created_at",
      responsive: ["xl"],
      sorter: (a, b) => a.created_at.localeCompare(b.created_at),
      render: (value) => dayjs(value).format("DD MMM YYYY")
    },
    {
      title: "Actions",
      width: 150,
      render: (_, record) => (
        <Space>
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/families/${record.id}`)} />
          {canWriteFamilies(roleNames) && (
            <Button icon={<EditOutlined />} onClick={() => navigate(`/families/${record.id}/edit`)} />
          )}
          {canDeleteFamilies(roleNames) && (
            <Popconfirm
              title="Delete family?"
              okText="Delete"
              okButtonProps={{ danger: true }}
              onConfirm={() => deleteMutation.mutate(record.id)}
            >
              <Button danger icon={<DeleteOutlined />} />
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Families</Typography.Title>
          <Typography.Text type="secondary">Manage family profiles, members, addresses, and service interests.</Typography.Text>
        </div>
        {canWriteFamilies(roleNames) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/families/new")}>
            New Family
          </Button>
        )}
      </div>
      <div className="family-toolbar">
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search name, phone, email, or code"
          value={search}
          onChange={(event) => {
            setPage(1);
            setSearch(event.target.value);
          }}
          allowClear
        />
        <Select
          placeholder="Status"
          value={status}
          onChange={(value) => {
            setPage(1);
            setStatus(value);
          }}
          allowClear
          options={familyStatuses.map((value) => ({ value, label: labelFromEnum(value) }))}
        />
        <Select
          placeholder="Source"
          value={source}
          onChange={(value) => {
            setPage(1);
            setSource(value);
          }}
          allowClear
          options={leadSources.map((value) => ({ value, label: labelFromEnum(value) }))}
        />
        <Select
          placeholder="Branch"
          value={branchId}
          onChange={(value) => {
            setPage(1);
            setBranchId(value);
          }}
          allowClear
          loading={branchesQuery.isLoading}
          options={(branchesQuery.data?.items ?? []).map((branch) => ({ value: branch.id, label: branch.name }))}
        />
        <RangePicker
          onChange={(values) => {
            setPage(1);
            setEddRange(values ? [values[0]!.format("YYYY-MM-DD"), values[1]!.format("YYYY-MM-DD")] : undefined);
          }}
        />
      </div>
      <Table
        rowKey="id"
        loading={familiesQuery.isLoading}
        dataSource={familiesQuery.data?.items ?? []}
        columns={columns}
        pagination={{
          current: page,
          pageSize: familiesQuery.data?.meta.page_size ?? 10,
          total: familiesQuery.data?.meta.total ?? 0,
          onChange: setPage
        }}
      />
    </Space>
  );
}
