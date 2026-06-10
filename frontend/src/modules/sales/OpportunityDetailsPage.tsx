import { ArrowLeftOutlined, CheckOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Descriptions, Form, Input, List, Modal, Select, Space, Tag, Timeline, Typography, message } from "antd";
import dayjs from "dayjs";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { listUsers } from "../../api/identity";
import { createFollowUp, createOpportunityNote, getOpportunity, updateFollowUp } from "../../api/sales";
import { useAuth } from "../../contexts/AuthContext";
import type { FollowUpPayload } from "../../types/sales";
import { canWriteSales, followUpTypes, labelFromEnum, stageColor } from "./salesOptions";

export function OpportunityDetailsPage() {
  const { opportunityId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const roleNames = user?.roles.map((role) => role.name) ?? [];
  const [isFollowUpOpen, setIsFollowUpOpen] = useState(false);
  const [isNoteOpen, setIsNoteOpen] = useState(false);
  const [followUpForm] = Form.useForm<FollowUpPayload>();
  const [noteForm] = Form.useForm<{ note: string }>();
  const opportunityQuery = useQuery({
    queryKey: ["opportunities", opportunityId],
    queryFn: () => getOpportunity(opportunityId!),
    enabled: Boolean(opportunityId)
  });
  const usersQuery = useQuery({ queryKey: ["users", "followup-form"], queryFn: () => listUsers({ page: 1, page_size: 100 }) });
  const opportunity = opportunityQuery.data;
  const editable = canWriteSales(roleNames) && opportunity?.current_stage !== "BOOKED";

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

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>{opportunity?.family?.primary_contact_name ?? "Opportunity"}</Typography.Title>
          <Typography.Text type="secondary">{opportunity?.family?.family_code ?? "Loading opportunity"}</Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/sales/opportunities")}>Back</Button>
      </div>
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
