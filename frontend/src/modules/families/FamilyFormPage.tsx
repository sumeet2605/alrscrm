import { ArrowLeftOutlined, SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, DatePicker, Form, Input, InputNumber, Select, Space, Typography, message } from "antd";
import dayjs from "dayjs";
import { useEffect } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { createFamily, getFamily, updateFamily } from "../../api/families";
import { listBranches } from "../../api/identity";
import { useAuth } from "../../contexts/AuthContext";
import type { FamilyPayload } from "../../types/families";
import { canWriteFamilies, familyStatuses, labelFromEnum, leadSources, relationships, serviceTypes } from "./familyOptions";

interface FamilyFormValues extends Omit<FamilyPayload, "expected_delivery_date"> {
  expected_delivery_date?: dayjs.Dayjs | null;
}

const emptyFamily: Partial<FamilyFormValues> = {
  status: "INQUIRY",
  source: "OTHER",
  members: [],
  service_interests: []
};

function toPayload(values: FamilyFormValues): FamilyPayload {
  return {
    ...values,
    expected_delivery_date: values.expected_delivery_date?.format("YYYY-MM-DD") ?? null
  };
}

export function FamilyFormPage() {
  const { familyId } = useParams();
  const isEdit = Boolean(familyId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [form] = Form.useForm<FamilyFormValues>();

  const familyQuery = useQuery({
    queryKey: ["families", familyId],
    queryFn: () => getFamily(familyId!),
    enabled: isEdit
  });

  const branchesQuery = useQuery({
    queryKey: ["branches", "family-form"],
    queryFn: () => listBranches({ page: 1, page_size: 100 })
  });

  useEffect(() => {
    if (!isEdit) {
      form.setFieldsValue({
        ...emptyFamily,
        organization_id: user?.organization_id,
        branch_id: user?.branch_id ?? undefined
      } as FamilyFormValues);
      return;
    }
    if (familyQuery.data) {
      form.setFieldsValue({
        ...familyQuery.data,
        expected_delivery_date: familyQuery.data.expected_delivery_date
          ? dayjs(familyQuery.data.expected_delivery_date)
          : null
      });
    }
  }, [familyQuery.data, form, isEdit, user?.branch_id, user?.organization_id]);

  const saveMutation = useMutation({
    mutationFn: (values: FamilyFormValues) =>
      isEdit ? updateFamily(familyId!, toPayload(values)) : createFamily(toPayload(values)),
    onSuccess: async (family) => {
      message.success(isEdit ? "Family updated" : "Family created");
      await queryClient.invalidateQueries({ queryKey: ["families"] });
      navigate(`/families/${family.id}`);
    }
  });

  if (!canWriteFamilies(roleNames)) {
    return <Navigate to="/families" replace />;
  }

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{isEdit ? "Edit Family" : "New Family"}</Typography.Title>
          <Typography.Text type="secondary">Capture the family profile used by bookings and delivery workflows.</Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(isEdit ? `/families/${familyId}` : "/families")}>
          Back
        </Button>
      </div>
      <Form
        form={form}
        layout="vertical"
        requiredMark={false}
        onFinish={(values) => saveMutation.mutate(values)}
      >
        <Card title="Profile" loading={familyQuery.isLoading}>
          <div className="form-grid">
            <Form.Item name="organization_id" hidden>
              <Input />
            </Form.Item>
            <Form.Item label="Branch" name="branch_id" rules={[{ required: true, message: "Branch is required" }]}>
              <Select
                loading={branchesQuery.isLoading}
                options={(branchesQuery.data?.items ?? []).map((branch) => ({ value: branch.id, label: branch.name }))}
              />
            </Form.Item>
            <Form.Item label="Primary Contact" name="primary_contact_name" rules={[{ required: true, message: "Primary contact is required" }]}>
              <Input />
            </Form.Item>
            <Form.Item label="Primary Phone" name="primary_contact_phone" rules={[{ required: true, message: "Primary phone is required" }]}>
              <Input />
            </Form.Item>
            <Form.Item label="Primary Email" name="primary_contact_email" rules={[{ type: "email", message: "Enter a valid email" }]}>
              <Input />
            </Form.Item>
            <Form.Item label="Partner" name="partner_name">
              <Input />
            </Form.Item>
            <Form.Item label="Partner Phone" name="partner_phone">
              <Input />
            </Form.Item>
            <Form.Item label="Partner Email" name="partner_email" rules={[{ type: "email", message: "Enter a valid email" }]}>
              <Input />
            </Form.Item>
            <Form.Item label="City" name="city">
              <Input />
            </Form.Item>
            <Form.Item label="Expected Delivery Date" name="expected_delivery_date">
              <DatePicker className="full-width-control" />
            </Form.Item>
            <Form.Item label="Source" name="source">
              <Select options={leadSources.map((value) => ({ value, label: labelFromEnum(value) }))} />
            </Form.Item>
            <Form.Item label="Status" name="status">
              <Select options={familyStatuses.map((value) => ({ value, label: labelFromEnum(value) }))} />
            </Form.Item>
          </div>
          <Form.Item label="Notes" name="notes">
            <Input.TextArea rows={4} />
          </Form.Item>
        </Card>

        <Card title="Family Members">
          <Form.List name="members">
            {(fields, { add, remove }) => (
              <Space direction="vertical" size={12} className="page-stack">
                {fields.map((field) => (
                  <div className="inline-form-row" key={field.key}>
                    <Form.Item name={[field.name, "name"]} rules={[{ required: true, message: "Name is required" }]}>
                      <Input placeholder="Name" />
                    </Form.Item>
                    <Form.Item name={[field.name, "relationship"]} rules={[{ required: true, message: "Relationship is required" }]}>
                      <Select placeholder="Relationship" options={relationships.map((value) => ({ value, label: labelFromEnum(value) }))} />
                    </Form.Item>
                    <Form.Item name={[field.name, "date_of_birth"]}>
                      <Input placeholder="Date of birth YYYY-MM-DD" />
                    </Form.Item>
                    <Button onClick={() => remove(field.name)}>Remove</Button>
                  </div>
                ))}
                <Button onClick={() => add({ relationship: "BABY" })}>Add Member</Button>
              </Space>
            )}
          </Form.List>
        </Card>

        <Card title="Address">
          <div className="form-grid">
            <Form.Item label="Address Line 1" name={["address", "address_line_1"]}>
              <Input />
            </Form.Item>
            <Form.Item label="Address Line 2" name={["address", "address_line_2"]}>
              <Input />
            </Form.Item>
            <Form.Item label="City" name={["address", "city"]}>
              <Input />
            </Form.Item>
            <Form.Item label="State" name={["address", "state"]}>
              <Input />
            </Form.Item>
            <Form.Item label="Country" name={["address", "country"]}>
              <Input />
            </Form.Item>
            <Form.Item label="Postal Code" name={["address", "postal_code"]}>
              <Input />
            </Form.Item>
          </div>
        </Card>

        <Card title="Service Interests">
          <Form.List name="service_interests">
            {(fields, { add, remove }) => (
              <Space direction="vertical" size={12} className="page-stack">
                {fields.map((field) => (
                  <div className="inline-form-row" key={field.key}>
                    <Form.Item name={[field.name, "service_type"]} rules={[{ required: true, message: "Service is required" }]}>
                      <Select placeholder="Service" options={serviceTypes.map((value) => ({ value, label: labelFromEnum(value) }))} />
                    </Form.Item>
                    <Form.Item name={[field.name, "priority"]}>
                      <InputNumber min={1} max={5} placeholder="Priority" className="full-width-control" />
                    </Form.Item>
                    <Form.Item name={[field.name, "notes"]}>
                      <Input placeholder="Notes" />
                    </Form.Item>
                    <Button onClick={() => remove(field.name)}>Remove</Button>
                  </div>
                ))}
                <Button onClick={() => add({ service_type: "NEWBORN", priority: 1 })}>Add Service</Button>
              </Space>
            )}
          </Form.List>
        </Card>

        <div className="form-actions">
          <Button onClick={() => navigate("/families")}>Cancel</Button>
          <Button type="primary" icon={<SaveOutlined />} htmlType="submit" loading={saveMutation.isPending}>
            Save Family
          </Button>
        </div>
      </Form>
    </Space>
  );
}
