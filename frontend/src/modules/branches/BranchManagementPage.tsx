import { EditOutlined, PlusOutlined, SearchOutlined, StopOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  App
} from "antd";
import { useMemo, useState } from "react";

import {
  createBranch,
  deactivateBranch,
  listBranches,
  updateBranch
} from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import type { Branch, BranchPayload } from "../../types/identity";

const emptyBranch: Partial<BranchPayload> = {
  is_active: true
};

export function BranchManagementPage() {
  const { user } = useAuth();
  const { message } = App.useApp();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const debouncedSearch = useDebouncedValue(search);
  const queryClient = useQueryClient();
  const [form] = Form.useForm<BranchPayload>();

  const branchesQuery = useQuery({
    queryKey: ["branches", page],
    queryFn: () => listBranches({ page, page_size: 10 })
  });

  const filteredBranches = useMemo(() => {
    const items = branchesQuery.data?.items ?? [];
    if (!debouncedSearch.trim()) {
      return items;
    }
    const needle = debouncedSearch.toLowerCase();
    return items.filter((branch) =>
      [branch.name, branch.code, branch.city, branch.email ?? ""].some((value) =>
        value.toLowerCase().includes(needle)
      )
    );
  }, [branchesQuery.data?.items, debouncedSearch]);

  const saveMutation = useMutation({
    mutationFn: (payload: BranchPayload) =>
      editingBranch ? updateBranch(editingBranch.id, payload) : createBranch(payload),
    onSuccess: async () => {
      message.success(editingBranch ? "Branch updated" : "Branch created");
      setIsModalOpen(false);
      setEditingBranch(null);
      form.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["branches"] });
    }
  });

  const deactivateMutation = useMutation({
    mutationFn: deactivateBranch,
    onSuccess: async () => {
      message.success("Branch deactivated");
      await queryClient.invalidateQueries({ queryKey: ["branches"] });
    }
  });

  const openCreate = () => {
    setEditingBranch(null);
    form.setFieldsValue({
      ...emptyBranch,
      organization_id: user?.organization_id
    } as BranchPayload);
    setIsModalOpen(true);
  };

  const openEdit = (branch: Branch) => {
    setEditingBranch(branch);
    form.setFieldsValue(branch);
    setIsModalOpen(true);
  };

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Branches</Typography.Title>
          <Typography.Text type="secondary">Manage studio locations and contact details.</Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          New Branch
        </Button>
      </div>
      <div className="table-toolbar">
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search branches"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          allowClear
        />
      </div>
      <Table
        rowKey="id"
        loading={branchesQuery.isLoading}
        dataSource={filteredBranches}
        pagination={{
          current: page,
          pageSize: branchesQuery.data?.meta.page_size ?? 10,
          total: branchesQuery.data?.meta.total ?? 0,
          onChange: setPage
        }}
        columns={[
          { title: "Name", dataIndex: "name" },
          { title: "Code", dataIndex: "code", width: 120 },
          { title: "City", dataIndex: "city", width: 160 },
          { title: "Email", dataIndex: "email", responsive: ["lg"] },
          {
            title: "Status",
            dataIndex: "is_active",
            width: 120,
            render: (active: boolean) => <Tag color={active ? "green" : "red"}>{active ? "Active" : "Inactive"}</Tag>
          },
          {
            title: "Actions",
            width: 160,
            render: (_, branch) => (
              <Space>
                <Button icon={<EditOutlined />} onClick={() => openEdit(branch)} />
                <Popconfirm
                  title="Deactivate branch?"
                  okText="Deactivate"
                  okButtonProps={{ danger: true }}
                  onConfirm={() => deactivateMutation.mutate(branch.id)}
                >
                  <Button danger icon={<StopOutlined />} />
                </Popconfirm>
              </Space>
            )
          }
        ]}
      />
      <Modal
        title={editingBranch ? "Edit Branch" : "Create Branch"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saveMutation.isPending}
        destroyOnClose
      >
        <Form form={form} layout="vertical" requiredMark={false} onFinish={(values) => saveMutation.mutate(values)}>
          <Form.Item name="organization_id" hidden>
            <Input />
          </Form.Item>
          <Form.Item label="Name" name="name" rules={[{ required: true, message: "Name is required" }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Code" name="code" rules={[{ required: true, message: "Code is required" }]}>
            <Input />
          </Form.Item>
          <Form.Item label="City" name="city" rules={[{ required: true, message: "City is required" }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Address" name="address">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item label="Phone" name="phone">
            <Input />
          </Form.Item>
          <Form.Item label="Email" name="email" rules={[{ type: "email", message: "Enter a valid email" }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Active" name="is_active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
