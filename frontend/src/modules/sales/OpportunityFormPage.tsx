import { ArrowLeftOutlined, SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, DatePicker, Form, Input, InputNumber, Select, Space, Typography, message } from "antd";
import dayjs from "dayjs";
import { Navigate, useNavigate } from "react-router-dom";

import { listFamilies } from "../../api/families";
import { listUsers } from "../../api/identity";
import { createOpportunity, listLostReasons } from "../../api/sales";
import { useAuth } from "../../contexts/AuthContext";
import type { OpportunityPayload } from "../../types/sales";
import { canWriteSales, labelFromEnum, opportunityStages, opportunityTypes } from "./salesOptions";

interface OpportunityFormValues extends Omit<OpportunityPayload, "expected_booking_date"> {
  expected_booking_date?: dayjs.Dayjs | null;
}

export function OpportunityFormPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [form] = Form.useForm<OpportunityFormValues>();
  const familiesQuery = useQuery({ queryKey: ["families", "opportunity-form"], queryFn: () => listFamilies({ page: 1, page_size: 100 }) });
  const usersQuery = useQuery({ queryKey: ["users", "opportunity-form"], queryFn: () => listUsers({ page: 1, page_size: 100 }) });
  const lostReasonsQuery = useQuery({ queryKey: ["lost-reasons"], queryFn: listLostReasons });

  const saveMutation = useMutation({
    mutationFn: (values: OpportunityFormValues) =>
      createOpportunity({
        ...values,
        expected_booking_date: values.expected_booking_date?.format("YYYY-MM-DD") ?? null
      }),
    onSuccess: async (opportunity) => {
      message.success("Opportunity created");
      await queryClient.invalidateQueries({ queryKey: ["opportunities"] });
      navigate(`/sales/opportunities/${opportunity.id}`);
    }
  });

  if (!canWriteSales(roleNames)) {
    return <Navigate to="/sales/opportunities" replace />;
  }

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>New Opportunity</Typography.Title>
          <Typography.Text type="secondary">Create a sales opportunity linked to an existing family profile.</Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/sales/opportunities")}>Back</Button>
      </div>
      <Card>
        <Form
          form={form}
          layout="vertical"
          requiredMark={false}
          initialValues={{
            organization_id: user?.organization_id,
            branch_id: user?.branch_id,
            assigned_to_user_id: user?.id,
            current_stage: "NEW",
            probability: 0,
            estimated_value: "20000.00"
          }}
          onFinish={(values) => saveMutation.mutate(values)}
        >
          <Form.Item name="organization_id" hidden><Input /></Form.Item>
          <Form.Item name="branch_id" hidden><Input /></Form.Item>
          <div className="form-grid">
            <Form.Item label="Family" name="family_id" rules={[{ required: true, message: "Family is required" }]}>
              <Select
                showSearch
                optionFilterProp="label"
                options={(familiesQuery.data?.items ?? []).map((family) => ({
                  value: family.id,
                  label: `${family.family_code} · ${family.primary_contact_name} · ${family.primary_contact_phone}`
                }))}
              />
            </Form.Item>
            <Form.Item label="Assigned User" name="assigned_to_user_id" rules={[{ required: true }]}>
              <Select options={(usersQuery.data?.items ?? []).map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))} />
            </Form.Item>
            <Form.Item label="Type" name="opportunity_type" rules={[{ required: true }]}>
              <Select options={opportunityTypes.map((value) => ({ value, label: labelFromEnum(value) }))} />
            </Form.Item>
            <Form.Item label="Stage" name="current_stage" rules={[{ required: true }]}>
              <Select options={opportunityStages.map((value) => ({ value, label: labelFromEnum(value) }))} />
            </Form.Item>
            <Form.Item label="Estimated Value" name="estimated_value" rules={[{ required: true }]}>
              <InputNumber min={0} className="full-width-control" />
            </Form.Item>
            <Form.Item label="Probability" name="probability">
              <InputNumber min={0} max={100} className="full-width-control" />
            </Form.Item>
            <Form.Item label="Expected Booking" name="expected_booking_date">
              <DatePicker className="full-width-control" />
            </Form.Item>
            <Form.Item label="Lost Reason" name="lost_reason_id">
              <Select allowClear options={(lostReasonsQuery.data ?? []).map((reason) => ({ value: reason.id, label: reason.name }))} />
            </Form.Item>
          </div>
          <Form.Item label="Notes" name="notes">
            <Input.TextArea rows={4} />
          </Form.Item>
          <div className="form-actions">
            <Button onClick={() => navigate("/sales/opportunities")}>Cancel</Button>
            <Button type="primary" icon={<SaveOutlined />} htmlType="submit" loading={saveMutation.isPending}>Save Opportunity</Button>
          </div>
        </Form>
      </Card>
    </Space>
  );
}
