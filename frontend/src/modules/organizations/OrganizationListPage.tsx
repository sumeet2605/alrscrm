import {
  CheckCircleOutlined,
  EyeOutlined,
  PlusOutlined,
  SearchOutlined,
  StopOutlined
} from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Input, Popconfirm, Space, Table, Tag, Typography } from "antd";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  activateOrganization,
  deactivateOrganization,
  listOrganizations
} from "../../api/identity";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";

export function OrganizationListPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);

  const organizationsQuery = useQuery({
    queryKey: ["organizations", page],
    queryFn: () => listOrganizations({ page, page_size: 10 })
  });

  const filteredOrganizations = useMemo(() => {
    const items = organizationsQuery.data?.items ?? [];
    const needle = debouncedSearch.trim().toLowerCase();
    if (!needle) {
      return items;
    }
    return items.filter((organization) =>
      [organization.name, organization.code].some((value) =>
        value.toLowerCase().includes(needle)
      )
    );
  }, [debouncedSearch, organizationsQuery.data?.items]);

  const activateMutation = useMutation({
    mutationFn: activateOrganization,
    onSuccess: async () => {
      message.success("Organization activated");
      await queryClient.invalidateQueries({ queryKey: ["organizations"] });
    }
  });

  const deactivateMutation = useMutation({
    mutationFn: deactivateOrganization,
    onSuccess: async () => {
      message.success("Organization deactivated");
      await queryClient.invalidateQueries({ queryKey: ["organizations"] });
    }
  });

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Organizations</Typography.Title>
          <Typography.Text type="secondary">
            Manage SaaS customer tenants and onboarding status.
          </Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/organizations/new")}>
          New Organization
        </Button>
      </div>
      <div className="table-toolbar">
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search organizations"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          allowClear
        />
      </div>
      <Table
        rowKey="id"
        loading={organizationsQuery.isLoading}
        dataSource={filteredOrganizations}
        pagination={{
          current: page,
          pageSize: organizationsQuery.data?.meta.page_size ?? 10,
          total: organizationsQuery.data?.meta.total ?? 0,
          onChange: setPage
        }}
        columns={[
          {
            title: "Organization",
            render: (_, organization) => (
              <div>
                <Typography.Text strong>{organization.name}</Typography.Text>
                <Typography.Text className="table-subtext">{organization.code}</Typography.Text>
              </div>
            )
          },
          {
            title: "Status",
            dataIndex: "is_active",
            width: 120,
            render: (active: boolean) => (
              <Tag color={active ? "green" : "red"}>{active ? "Active" : "Inactive"}</Tag>
            )
          },
          {
            title: "Created",
            dataIndex: "created_at",
            responsive: ["lg"],
            render: (value: string) => new Date(value).toLocaleDateString()
          },
          {
            title: "Actions",
            width: 200,
            render: (_, organization) => (
              <Space>
                <Button
                  aria-label="View organization"
                  icon={<EyeOutlined />}
                  onClick={() => navigate(`/organizations/${organization.id}`)}
                />
                {organization.is_active ? (
                  <Popconfirm
                    title="Deactivate organization?"
                    okText="Deactivate"
                    okButtonProps={{ danger: true }}
                    onConfirm={() => deactivateMutation.mutate(organization.id)}
                  >
                    <Button danger aria-label="Deactivate organization" icon={<StopOutlined />} />
                  </Popconfirm>
                ) : (
                  <Button
                    aria-label="Activate organization"
                    icon={<CheckCircleOutlined />}
                    onClick={() => activateMutation.mutate(organization.id)}
                  />
                )}
              </Space>
            )
          }
        ]}
      />
    </Space>
  );
}

