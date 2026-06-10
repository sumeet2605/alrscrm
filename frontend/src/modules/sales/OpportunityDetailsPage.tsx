import { ArrowLeftOutlined, CheckOutlined, EditOutlined, PlusOutlined, SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, DatePicker, Descriptions, Form, Input, InputNumber, List, Modal, Select, Space, Tag, Timeline, Typography, message } from "antd";
import dayjs from "dayjs";
import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";

import { listUsers } from "../../api/identity";
import { createFollowUp, createOpportunityNote, getOpportunity, listLostReasons, updateFollowUp, updateOpportunity } from "../../api/sales";
import { useAuth } from "../../contexts/AuthContext";
import type { FollowUpPayload, OpportunityUpdatePayload } from "../../types/sales";
import { canWriteSales, followUpTypes, labelFromEnum, opportunityStages, opportunityTypes, stageColor } from "./salesOptions";

interface OpportunityEditValues extends Omit<OpportunityUpdatePayload, "expected_booking_date"> {
  expected_booking_date?: dayjs.Dayjs | null;
}

export function OpportunityDetailsPage() {
  const { opportunityId } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const isEditing = searchParams.get("edit") === "1";
  const [isFollowUpOpen, setIsFollowUpOpen] = useState(false);
  const [isNoteOpen, setIsNoteOpen] = useState(false);
  const [followUpForm] = Form.useForm<FollowUpPayload>();
  const [noteForm] = Form.useForm<{ note: string }>();
  const [editForm] = Form.useForm<OpportunityEditValues>();
  const opportunityQuery = useQuery({
    queryKey: ["opportunities", opportunityId],
    queryFn: () => getOpportunity(opportunityId!),
    enabled: Boolean(opportunityId)
  });
  const usersQuery = useQuery({ queryKey: ["users", "followup-form"], queryFn: () => listUsers({ page: 1, page_size: 100 }) });
  const lostReasonsQuery = useQuery({ queryKey: ["lost-reasons"], queryFn: listLostReasons });
  const opportunity = opportunityQuery.data;
  const editable = canWriteSales(roleNames) && opportunity?.current_stage !== "BOOKED";

  useEffect(() => {
    if (opportunity && isEditing) {
      editForm.setFieldsValue({
        branch_id: opportunity.branch_id,
        family_id: opportunity.family_id,
        assigned_to_user_id: opportunity.assigned_to_user_id,
        opportunity_type: opportunity.opportunity_type,
        current_stage: opportunity.current_stage,
        estimated_value: opportunity.estimated_value,
        probability: opportunity.probability,
        expected_booking_date: opportunity.expected_booking_date ? dayjs(opportunity.expected_booking_date) : null,
        lost_reason_id: opportunity.lost_reason_id,
        notes: opportunity.notes
      });
    }
  }, [editForm, isEditing, opportunity]);

  const followUpMutation = useMutation({
    mutationFn: createFollowUp,
    onSuccess: async () => {
      message.success("Follow-up created");
      setIsFollowUpOpen(false);
      followUpForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["opportunities", opportunityId] });
    }
  });
  const completeMutation = useMutation({
    mutationFn: (id: string) => updateFollowUp(id, { status: "COMPLETED" }),
    onSuccess: async () => {
      message.success("Follow-up completed");
      await queryClient.invalidateQueries({ queryKey: ["opportunities", opportunityId] });
    }
  });
  const noteMutation = useMutation({
    mutationFn: (note: string) => createOpportunityNote(opportunityId!, note),
    onSuccess: async () => {
      message.success("Note added");
      setIsNoteOpen(false);
      noteForm.resetFields();
      await queryClient.invalidateQueries({ queryKey: ["opportunities", opportunityId] });
    }
  });
  const editMutation = useMutation({
    mutationFn: (values: OpportunityEditValues) =>
      updateOpportunity(opportunityId!, {
        ...values,
        expected_booking_date: values.expected_booking_date?.format("YYYY-MM-DD") ?? null
      }),
    onSuccess: async () => {
      message.success("Opportunity updated");
      setSearchParams({});
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["opportunities", opportunityId] }),
        queryClient.invalidateQueries({ queryKey: ["opportunities"] }),
        queryClient.invalidateQueries({ queryKey: ["sales"] })
      ]);
    }
  });

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{opportunity?.family?.primary_contact_name ?? "Opportunity"}</Typography.Title>
          <Typography.Text type="secondary">{opportunity?.family?.family_code ?? "Loading opportunity"}</Typography.Text>
        </div>
        <Space>
          {editable && !isEditing && <Button icon={<EditOutlined />} onClick={() => setSearchParams({ edit: "1" })}>Edit</Button>}
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/sales/opportunities")}>Back</Button>
        </Space>
      </div>
      {editable && isEditing && (
        <Card title="Edit Opportunity">
          <Form form={editForm} layout="vertical" requiredMark={false} onFinish={(values) => editMutation.mutate(values)}>
            <Form.Item name="branch_id" hidden><Input /></Form.Item>
            <Form.Item name="family_id" hidden><Input /></Form.Item>
            <div className="form-grid">
              <Form.Item label="Assigned User" name="assigned_to_user_id" rules={[{ required: true, message: "Assigned user is required" }]}>
                <Select options={(usersQuery.data?.items ?? []).map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))} />
              </Form.Item>
              <Form.Item label="Type" name="opportunity_type" rules={[{ required: true, message: "Type is required" }]}>
                <Select options={opportunityTypes.map((value) => ({ value, label: labelFromEnum(value) }))} />
              </Form.Item>
              <Form.Item label="Stage" name="current_stage" rules={[{ required: true, message: "Stage is required" }]}>
                <Select options={opportunityStages.map((value) => ({ value, label: labelFromEnum(value) }))} />
              </Form.Item>
              <Form.Item label="Estimated Value" name="estimated_value" rules={[{ required: true, message: "Estimated value is required" }]}>
                <InputNumber min={0} className="full-width-control" />
              </Form.Item>
              <Form.Item label="Probability" name="probability" rules={[{ type: "number", min: 0, max: 100, message: "Probability must be between 0 and 100" }]}>
                <InputNumber min={0} max={100} className="full-width-control" />
              </Form.Item>
              <Form.Item label="Expected Booking" name="expected_booking_date">
                <DatePicker className="full-width-control" />
              </Form.Item>
              <Form.Item
                label="Lost Reason"
                name="lost_reason_id"
                dependencies={["current_stage"]}
                rules={[
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (getFieldValue("current_stage") !== "LOST" || value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error("Lost reason is required when stage is Lost"));
                    }
                  })
                ]}
              >
                <Select allowClear options={(lostReasonsQuery.data ?? []).map((reason) => ({ value: reason.id, label: reason.name }))} />
              </Form.Item>
            </div>
            <Form.Item label="Notes" name="notes"><Input.TextArea rows={4} /></Form.Item>
            <Form.Item label="Stage Change Notes" name="stage_change_notes"><Input.TextArea rows={3} /></Form.Item>
            <div className="form-actions">
              <Button onClick={() => setSearchParams({})}>Cancel</Button>
              <Button type="primary" icon={<SaveOutlined />} htmlType="submit" loading={editMutation.isPending}>Save Changes</Button>
            </div>
          </Form>
        </Card>
      )}
      <Card loading={opportunityQuery.isLoading} title="Opportunity Information">
        {opportunity && (
          <Descriptions bordered size="small" column={{ xs: 1, md: 2, xl: 3 }}>
            <Descriptions.Item label="Stage"><Tag color={stageColor(opportunity.current_stage)}>{labelFromEnum(opportunity.current_stage)}</Tag></Descriptions.Item>
            <Descriptions.Item label="Type">{labelFromEnum(opportunity.opportunity_type)}</Descriptions.Item>
            <Descriptions.Item label="Estimated Value">₹{Number(opportunity.estimated_value).toLocaleString("en-IN")}</Descriptions.Item>
            <Descriptions.Item label="Probability">{opportunity.probability}%</Descriptions.Item>
            <Descriptions.Item label="Expected Booking">{opportunity.expected_booking_date ? dayjs(opportunity.expected_booking_date).format("DD MMM YYYY") : "-"}</Descriptions.Item>
            <Descriptions.Item label="Assigned">{opportunity.assigned_to_user ? `${opportunity.assigned_to_user.first_name} ${opportunity.assigned_to_user.last_name}` : "-"}</Descriptions.Item>
            <Descriptions.Item label="Phone">{opportunity.family?.primary_contact_phone}</Descriptions.Item>
            <Descriptions.Item label="Email">{opportunity.family?.primary_contact_email || "-"}</Descriptions.Item>
            <Descriptions.Item label="City">{opportunity.family?.city || "-"}</Descriptions.Item>
          </Descriptions>
        )}
      </Card>
      <div className="details-grid">
        <Card title="Follow Ups" extra={editable ? <Button icon={<PlusOutlined />} onClick={() => setIsFollowUpOpen(true)}>Add</Button> : null}>
          <List
            dataSource={opportunity?.followups ?? []}
            locale={{ emptyText: "No follow-ups" }}
            renderItem={(item) => (
              <List.Item
                actions={editable && item.status !== "COMPLETED" ? [<Button key="complete" icon={<CheckOutlined />} onClick={() => completeMutation.mutate(item.id)}>Complete</Button>] : []}
              >
                <List.Item.Meta
                  title={`${labelFromEnum(item.followup_type)} · ${dayjs(item.due_date).format("DD MMM YYYY")}`}
                  description={item.notes || labelFromEnum(item.status)}
                />
                <Tag>{labelFromEnum(item.status)}</Tag>
              </List.Item>
            )}
          />
        </Card>
        <Card title="Notes" extra={editable ? <Button icon={<PlusOutlined />} onClick={() => setIsNoteOpen(true)}>Add</Button> : null}>
          <List
            dataSource={opportunity?.opportunity_notes ?? []}
            locale={{ emptyText: "No notes" }}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta title={dayjs(item.created_at).format("DD MMM YYYY, h:mm A")} description={item.note} />
              </List.Item>
            )}
          />
        </Card>
      </div>
      <Card title="Stage History">
        <Timeline
          items={(opportunity?.stage_history ?? []).map((item) => ({
            children: `${item.from_stage ? `${labelFromEnum(item.from_stage)} → ` : ""}${labelFromEnum(item.to_stage)} · ${dayjs(item.created_at).format("DD MMM YYYY, h:mm A")}${item.notes ? ` · ${item.notes}` : ""}`
          }))}
        />
      </Card>
      <Modal title="Add Follow-up" open={isFollowUpOpen} onCancel={() => setIsFollowUpOpen(false)} onOk={() => followUpForm.submit()} confirmLoading={followUpMutation.isPending}>
        <Form form={followUpForm} layout="vertical" requiredMark={false} initialValues={{ opportunity_id: opportunityId, assigned_to_user_id: user?.id, followup_type: "WHATSAPP", status: "PENDING" }} onFinish={(values) => followUpMutation.mutate(values)}>
          <Form.Item name="opportunity_id" hidden><Input /></Form.Item>
          <Form.Item label="Assigned User" name="assigned_to_user_id" rules={[{ required: true }]}><Select options={(usersQuery.data?.items ?? []).map((item) => ({ value: item.id, label: `${item.first_name} ${item.last_name}` }))} /></Form.Item>
          <Form.Item label="Type" name="followup_type" rules={[{ required: true }]}><Select options={followUpTypes.map((value) => ({ value, label: labelFromEnum(value) }))} /></Form.Item>
          <Form.Item label="Due Date" name="due_date" rules={[{ required: true }]}><Input type="date" /></Form.Item>
          <Form.Item label="Notes" name="notes"><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
      <Modal title="Add Note" open={isNoteOpen} onCancel={() => setIsNoteOpen(false)} onOk={() => noteForm.submit()} confirmLoading={noteMutation.isPending}>
        <Form form={noteForm} layout="vertical" requiredMark={false} onFinish={(values) => noteMutation.mutate(values.note)}>
          <Form.Item label="Note" name="note" rules={[{ required: true, message: "Note is required" }]}><Input.TextArea rows={4} /></Form.Item>
        </Form>
      </Modal>
    </Space>
  );
}
