import { DeleteOutlined, EditOutlined, EyeOutlined, PlusOutlined, SearchOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Input, Popconfirm, Select, Space, Table, Tag, Typography } from "antd";
import type { TableProps } from "antd";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { deleteOpportunity, listLostReasons, listOpportunities } from "../../api/sales";
import { listUsers } from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import type { Opportunity, OpportunityStage, OpportunityType } from "../../types/sales";
import { canDeleteSales, canWriteSales, labelFromEnum, opportunityStages, opportunityTypes, stageColor } from "./salesOptions";

export function OpportunityListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [stage, setStage] = useState<OpportunityStage | undefined>();
  const [opportunityType, setOpportunityType] = useState<OpportunityType | undefined>();
  const [assignedToUserId, setAssignedToUserId] = useState<string | undefined>();
  const [lostReasonId, setLostReasonId] = useState<string | undefined>();
  const debouncedSearch = useDebouncedValue(search);

  const opportunitiesQuery = useQuery({
    queryKey: ["opportunities", page, debouncedSearch, stage, opportunityType, assignedToUserId, lostReasonId],
    queryFn: () =>
      listOpportunities({
        page,
        page_size: 10,
        search: debouncedSearch || undefined,
        stage,
        opportunity_type: opportunityType,
        assigned_to_user_id: assignedToUserId,
        lost_reason_id: lostReasonId
      })
  });
  const usersQuery = useQuery({ queryKey: ["users", "sales-filter"], queryFn: () => listUsers({ page: 1, page_size: 100 }) });
  const lostReasonsQuery = useQuery({ queryKey: ["lost-reasons"], queryFn: listLostReasons });
  const deleteMutation = useMutation({
    mutationFn: deleteOpportunity,
    onSuccess: async () => {
      message.success("Opportunity deleted");
      await queryClient.invalidateQueries({ queryKey: ["opportunities"] });
    }
  });

  const columns: TableProps<Opportunity>["columns"] = [
    {
      title: "Family",
      render: (_, item) => (
        <div>
          <Button type="link" onClick={() => navigate(`/sales/opportunities/${item.id}`)}>
            {item.family?.primary_contact_name}
          </Button>
          <Typography.Text className="table-subtext">{item.family?.family_code} · {item.family?.primary_contact_phone}</Typography.Text>
        </div>
      )
    },
    { title: "Type", dataIndex: "opportunity_type", render: (value) => labelFromEnum(value) },
    {
      title: "Stage",
      dataIndex: "current_stage",
      render: (value: OpportunityStage) => <Tag color={stageColor(value)}>{labelFromEnum(value)}</Tag>
    },
    { title: "Value", dataIndex: "estimated_value", sorter: (a, b) => Number(a.estimated_value) - Number(b.estimated_value), render: (value) => `₹${Number(value).toLocaleString("en-IN")}` },
    { title: "Assigned", responsive: ["lg"], render: (_, item) => item.assigned_to_user ? `${item.assigned_to_user.first_name} ${item.assigned_to_user.last_name}` : "-" },
    { title: "Expected Booking", dataIndex: "expected_booking_date", responsive: ["lg"], render: (value) => value ? dayjs(value).format("DD MMM YYYY") : "-" },
    {
      title: "Actions",
      width: 150,
      render: (_, item) => (
        <Space>
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/sales/opportunities/${item.id}`)} />
          {canWriteSales(roleNames) && item.current_stage !== "BOOKED" && (
            <Button icon={<EditOutlined />} onClick={() => navigate(`/sales/opportunities/${item.id}?edit=1`)} />
          )}
          {canDeleteSales(roleNames) && item.current_stage !== "BOOKED" && (
            <Popconfirm title="Delete opportunity?" okText="Delete" okButtonProps={{ danger: true }} onConfirm={() => deleteMutation.mutate(item.id)}>
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
          <Typography.Title level={2}>Opportunities</Typography.Title>
          <Typography.Text type="secondary">Search, filter, and manage tracked sales opportunities.</Typography.Text>
        </div>
        {canWriteSales(roleNames) && <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/sales/opportunities/new")}>New Opportunity</Button>}
      </div>
      <div className="sales-toolbar">
        <Input prefix={<SearchOutlined />} placeholder="Search family, phone, code, or type" value={search} onChange={(event) => { setPage(1); setSearch(event.target.value); }} allowClear />
        <Select placeholder="Stage" value={stage} onChange={(value) => { setPage(1); setStage(value); }} allowClear options={opportunityStages.map((value) => ({ value, label: labelFromEnum(value) }))} />
        <Select placeholder="Type" value={opportunityType} onChange={(value) => { setPage(1); setOpportunityType(value); }} allowClear options={opportunityTypes.map((value) => ({ value, label: labelFromEnum(value) }))} />
        <Select placeholder="Assigned" value={assignedToUserId} onChange={(value) => { setPage(1); setAssignedToUserId(value); }} allowClear options={(usersQuery.data?.items ?? []).map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))} />
        <Select placeholder="Lost Reason" value={lostReasonId} onChange={(value) => { setPage(1); setLostReasonId(value); }} allowClear options={(lostReasonsQuery.data ?? []).map((item) => ({ value: item.id, label: item.name }))} />
      </div>
      <Table
        rowKey="id"
        loading={opportunitiesQuery.isLoading}
        dataSource={opportunitiesQuery.data?.items ?? []}
        columns={columns}
        pagination={{ current: page, pageSize: opportunitiesQuery.data?.meta.page_size ?? 10, total: opportunitiesQuery.data?.meta.total ?? 0, onChange: setPage }}
      />
    </Space>
  );
}
