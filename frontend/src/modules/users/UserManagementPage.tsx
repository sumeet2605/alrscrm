import { EditOutlined, PlusOutlined, SearchOutlined, StopOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Button,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  message
} from "antd";
import { useMemo, useState } from "react";

import {
  createUser,
  deactivateUser,
  listBranches,
  listRoles,
  listUsers,
  updateUser
} from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import type { User, UserPayload } from "../../types/identity";

type UserFormValues = Partial<UserPayload> & { password?: string };

export function UserManagementPage() {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState<string | undefined>();
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const debouncedSearch = useDebouncedValue(search);
  const queryClient = useQueryClient();
  const [form] = Form.useForm<UserFormValues>();

  const usersQuery = useQuery({
    queryKey: ["users", page],
    queryFn: () => listUsers({ page, page_size: 10 })
  });
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: listRoles });
  const branchesQuery = useQuery({
    queryKey: ["branches", "all"],
    queryFn: () => listBranches({ page: 1, page_size: 100 })
  });

  const filteredUsers = useMemo(() => {
    const items = usersQuery.data?.items ?? [];
    const needle = debouncedSearch.trim().toLowerCase();
    return items.filter((item) => {
      const matchesSearch =
        !needle ||
        [item.email, item.username ?? "", item.first_name, item.last_name].some((value) =>
          value.toLowerCase().includes(needle)
        );
      const matchesRole = !roleFilter || item.roles.some((role) => role.id === roleFilter);
      return matchesSearch && matchesRole;
    });
  }, [debouncedSearch, roleFilter, usersQuery.data?.items]);

  const saveMutation = useMutation({
    mutationFn: (payload: UserFormValues) => {
      const cleanedPayload = {
        ...payload,
        password: payload.password || undefined
      };
      return editingUser
        ? updateUser(editingUser.id, cleanedPayload)
        : createUser(cleanedPayload as UserPayload);
    },
    onSuccess: async () => {
      message.success(editingUser ? "User updated" : "User created");
      setIsModalOpen(false);
      setEditingUser(null);
      form.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["users"] });
    }
  });

  const deactivateMutation = useMutation({
    mutationFn: deactivateUser,
    onSuccess: async () => {
      message.success("User deactivated");
      await queryClient.invalidateQueries({ queryKey: ["users"] });
    }
  });

  const openCreate = () => {
    setEditingUser(null);
    form.setFieldsValue({
      organization_id: user?.organization_id,
      branch_id: user?.branch_id,
      is_active: true,
      role_ids: []
    });
    setIsModalOpen(true);
  };

  const openEdit = (targetUser: User) => {
    setEditingUser(targetUser);
    form.setFieldsValue({
      ...targetUser,
      password: "",
      role_ids: targetUser.roles.map((role) => role.id)
    });
    setIsModalOpen(true);
  };

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Users</Typography.Title>
          <Typography.Text type="secondary">Manage team access, roles, and account status.</Typography.Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
          New User
        </Button>
      </div>
      <div className="table-toolbar">
        <Input
          prefix={<SearchOutlined />}
          placeholder="Search users"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          allowClear
        />
        <Select
          allowClear
          placeholder="Filter by role"
          value={roleFilter}
          onChange={setRoleFilter}
          options={(rolesQuery.data ?? []).map((role) => ({ label: role.name, value: role.id }))}
        />
      </div>
      <Table
        rowKey="id"
        loading={usersQuery.isLoading}
        dataSource={filteredUsers}
        pagination={{
          current: page,
          pageSize: usersQuery.data?.meta.page_size ?? 10,
          total: usersQuery.data?.meta.total ?? 0,
          onChange: setPage
        }}
        columns={[
          {
            title: "User",
            render: (_, item) => (
              <div>
                <Typography.Text strong>
                  {item.first_name} {item.last_name}
                </Typography.Text>
                <Typography.Text className="table-subtext">{item.email}</Typography.Text>
              </div>
            )
          },
          {
            title: "Roles",
            dataIndex: "roles",
            render: (_, item) => (
              <Space wrap>
                {item.roles.map((role) => (
                  <Tag key={role.id}>{role.name}</Tag>
                ))}
              </Space>
            )
          },
          {
            title: "Status",
            dataIndex: "is_active",
            width: 120,
            render: (active: boolean) => <Tag color={active ? "green" : "red"}>{active ? "Active" : "Inactive"}</Tag>
          },
          {
            title: "Actions",
            width: 160,
            render: (_, item) => (
              <Space>
                <Button icon={<EditOutlined />} onClick={() => openEdit(item)} />
                <Popconfirm
                  title="Deactivate user?"
                  okText="Deactivate"
                  okButtonProps={{ danger: true }}
                  onConfirm={() => deactivateMutation.mutate(item.id)}
                >
                  <Button danger icon={<StopOutlined />} />
                </Popconfirm>
              </Space>
            )
          }
        ]}
      />
      <Modal
        title={editingUser ? "Edit User" : "Create User"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={saveMutation.isPending}
        width={720}
        destroyOnClose
      >
        <Form form={form} layout="vertical" requiredMark={false} onFinish={(values) => saveMutation.mutate(values)}>
          <Form.Item name="organization_id" hidden>
            <Input />
          </Form.Item>
          <Form.Item label="Branch" name="branch_id">
            <Select
              allowClear
              options={(branchesQuery.data?.items ?? []).map((branch) => ({
                label: branch.name,
                value: branch.id
              }))}
            />
          </Form.Item>
          <Form.Item label="Username" name="username">
            <Input />
          </Form.Item>
          <Form.Item label="Email" name="email" rules={[{ required: true }, { type: "email" }]}>
            <Input />
          </Form.Item>
          <Form.Item
            label="Password"
            name="password"
            rules={editingUser ? [] : [{ required: true, message: "Password is required" }]}
          >
            <Input.Password />
          </Form.Item>
          <div className="form-grid">
            <Form.Item label="First name" name="first_name" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item label="Last name" name="last_name" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
          </div>
          <Form.Item label="Phone" name="phone">
            <Input />
          </Form.Item>
          <Form.Item label="Roles" name="role_ids">
            <Select
              mode="multiple"
              options={(rolesQuery.data ?? []).map((role) => ({ label: role.name, value: role.id }))}
            />
          </Form.Item>
          <Form.Item label="Active" name="is_active" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
