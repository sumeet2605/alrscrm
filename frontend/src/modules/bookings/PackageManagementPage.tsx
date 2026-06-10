import { EditOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { App, Button, Form, Input, InputNumber, Modal, Select, Space, Table, Tag, Typography } from "antd";
import { useState } from "react";

import { createAddon, createPackage, listAddons, listPackages, updateAddon, updatePackage } from "../../api/bookings";
import { listBranches } from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import type { Package, PackageAddon, PackagePayload } from "../../types/bookings";
import { canManagePackages, labelFromEnum, serviceTypes } from "./bookingOptions";

type PackageFormValues = PackagePayload & { kind: "package" | "addon" };

export function PackageManagementPage() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [editing, setEditing] = useState<(Package | PackageAddon) & { kind: "package" | "addon" } | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [form] = Form.useForm<PackageFormValues>();
  const packagesQuery = useQuery({ queryKey: ["packages"], queryFn: listPackages });
  const addonsQuery = useQuery({ queryKey: ["addons"], queryFn: listAddons });
  const branchesQuery = useQuery({
    queryKey: ["branches", "package-management"],
    queryFn: () => listBranches({ page: 1, page_size: 100 })
  });
  const saveMutation = useMutation({
    mutationFn: async (values: PackageFormValues) => {
      const selectedBranch = branchesQuery.data?.items.find((branch) => branch.id === values.branch_id);
      const branchId = values.branch_id ?? user?.branch_id;
      const organizationId = selectedBranch?.organization_id ?? user!.organization_id;
      const payload = { ...values, organization_id: organizationId, branch_id: branchId! };
      if (editing?.kind === "package") return updatePackage(editing.id, payload);
      if (editing?.kind === "addon") return updateAddon(editing.id, payload);
      if (values.kind === "addon") return createAddon(payload);
      return createPackage(payload);
    },
    onSuccess: async () => {
      message.success("Catalog saved");
      setIsOpen(false);
      setEditing(null);
      form.resetFields();
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["packages"] }),
        queryClient.invalidateQueries({ queryKey: ["addons"] })
      ]);
    }
  });
  const openForm = (kind: "package" | "addon", item?: Package | PackageAddon) => {
    setEditing(item ? { ...item, kind } : null);
    form.setFieldsValue({
      kind,
      branch_id: item?.branch_id ?? user?.branch_id ?? branchesQuery.data?.items[0]?.id,
      ...(item ?? {}),
      service_type: "service_type" in (item ?? {}) ? (item as Package).service_type : "NEWBORN"
    });
    setIsOpen(true);
  };

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>Packages</Typography.Title>
          <Typography.Text type="secondary">Manage package and addon reference data.</Typography.Text>
        </div>
        {canManagePackages(roleNames) && <Button type="primary" icon={<PlusOutlined />} onClick={() => openForm("package")}>New Package</Button>}
      </div>
      <Table rowKey="id" title={() => "Packages"} dataSource={packagesQuery.data ?? []} loading={packagesQuery.isLoading} columns={[
        { title: "Name", dataIndex: "name" },
        { title: "Service", dataIndex: "service_type", render: labelFromEnum },
        { title: "Price", dataIndex: "price", render: (value) => `₹${Number(value).toLocaleString("en-IN")}` },
        { title: "Status", dataIndex: "is_active", render: (value) => <Tag color={value ? "green" : "red"}>{value ? "Active" : "Inactive"}</Tag> },
        { title: "Actions", render: (_, item) => canManagePackages(roleNames) ? <Button icon={<EditOutlined />} onClick={() => openForm("package", item)} /> : null }
      ]} />
      <Table rowKey="id" title={() => <Space>Addons {canManagePackages(roleNames) && <Button size="small" icon={<PlusOutlined />} onClick={() => openForm("addon")}>New Addon</Button>}</Space>} dataSource={addonsQuery.data ?? []} loading={addonsQuery.isLoading} columns={[
        { title: "Name", dataIndex: "name" },
        { title: "Price", dataIndex: "price", render: (value) => `₹${Number(value).toLocaleString("en-IN")}` },
        { title: "Status", dataIndex: "is_active", render: (value) => <Tag color={value ? "green" : "red"}>{value ? "Active" : "Inactive"}</Tag> },
        { title: "Actions", render: (_, item) => canManagePackages(roleNames) ? <Button icon={<EditOutlined />} onClick={() => openForm("addon", item)} /> : null }
      ]} />
      <Modal title={editing ? "Edit Catalog Item" : "New Catalog Item"} open={isOpen} onCancel={() => setIsOpen(false)} onOk={() => form.submit()} confirmLoading={saveMutation.isPending}>
        <Form form={form} layout="vertical" requiredMark={false} initialValues={{ kind: "package", is_active: true }} onFinish={(values) => saveMutation.mutate(values)}>
          <Form.Item label="Type" name="kind"><Select options={[{ value: "package", label: "Package" }, { value: "addon", label: "Addon" }]} /></Form.Item>
          <Form.Item label="Branch" name="branch_id" rules={[{ required: true, message: "Branch is required" }]}><Select options={(branchesQuery.data?.items ?? []).map((branch) => ({ value: branch.id, label: `${branch.name} · ${branch.city}` }))} /></Form.Item>
          <Form.Item label="Name" name="name" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item noStyle shouldUpdate={(previous, current) => previous.kind !== current.kind}>{({ getFieldValue }) => getFieldValue("kind") === "package" ? <Form.Item label="Service" name="service_type" rules={[{ required: true }]}><Select options={serviceTypes.map((value) => ({ value, label: labelFromEnum(value) }))} /></Form.Item> : null}</Form.Item>
          <Form.Item label="Price" name="price" rules={[{ required: true }]}><InputNumber min={0} className="full-width-control" /></Form.Item>
          <Form.Item label="Description" name="description"><Input.TextArea rows={3} /></Form.Item>
          <Form.Item label="Active" name="is_active"><Select options={[{ value: true, label: "Active" }, { value: false, label: "Inactive" }]} /></Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
