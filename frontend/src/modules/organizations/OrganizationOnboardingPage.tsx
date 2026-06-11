import { ArrowLeftOutlined, CheckOutlined } from "@ant-design/icons";
import { useMutation } from "@tanstack/react-query";
import {
  Alert,
  App,
  Button,
  Descriptions,
  Form,
  Input,
  Result,
  Space,
  Steps,
  Typography
} from "antd";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { onboardOrganization } from "../../api/identity";
import type { OrganizationOnboardingPayload, OrganizationOnboardingResult } from "../../types/identity";

type WizardValues = {
  organization_name: string;
  organization_code: string;
  timezone: string;
  organization_email?: string;
  organization_phone?: string;
  branch_name: string;
  owner_name: string;
  owner_email: string;
  owner_phone?: string;
};

const initialValues: Partial<WizardValues> = {
  timezone: "Asia/Kolkata",
  branch_name: "Main Studio"
};

function buildPayload(values: WizardValues): OrganizationOnboardingPayload {
  return {
    organization: {
      name: values.organization_name,
      code: values.organization_code,
      timezone: values.timezone,
      email: values.organization_email || null,
      phone: values.organization_phone || null
    },
    branch: {
      name: values.branch_name
    },
    owner: {
      name: values.owner_name,
      email: values.owner_email,
      phone: values.owner_phone || null
    }
  };
}

export function OrganizationOnboardingPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const [form] = Form.useForm<WizardValues>();
  const [step, setStep] = useState(0);
  const [result, setResult] = useState<OrganizationOnboardingResult | null>(null);

  const onboardingMutation = useMutation({
    mutationFn: onboardOrganization,
    onSuccess: (data) => {
      setResult(data);
      message.success("Organization onboarded");
    }
  });

  const values = Form.useWatch([], form) ?? initialValues;
  const reviewPayload = useMemo(
    () => buildPayload({ ...initialValues, ...values } as WizardValues),
    [values]
  );

  const next = async () => {
    const fieldGroups: Array<Array<keyof WizardValues>> = [
      ["organization_name", "organization_code", "timezone", "organization_email", "organization_phone"],
      ["branch_name"],
      ["owner_name", "owner_email", "owner_phone"],
      []
    ];
    await form.validateFields(fieldGroups[step]);
    setStep((current) => current + 1);
  };

  const submit = async () => {
    const formValues = await form.validateFields();
    onboardingMutation.mutate(buildPayload(formValues));
  };

  if (result) {
    return (
      <Result
        status="success"
        title="Organization created"
        subTitle={`${result.organization.name} is ready with its default branch and Owner account.`}
        extra={
          <Space direction="vertical" size={16}>
            <Alert
              type="warning"
              showIcon
              message="Owner temporary password"
              description={result.owner_temporary_password}
            />
            <Space>
              <Button onClick={() => navigate("/organizations")}>Organizations</Button>
              <Button type="primary" onClick={() => navigate(`/organizations/${result.organization.id}`)}>
                View Organization
              </Button>
            </Space>
          </Space>
        }
      />
    );
  }

  return (
    <Space direction="vertical" size={16} className="page-stack">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>New Organization</Typography.Title>
          <Typography.Text type="secondary">
            Create a customer tenant with a default branch and owner user.
          </Typography.Text>
        </div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/organizations")}>
          Back
        </Button>
      </div>
      <Steps
        current={step}
        items={[
          { title: "Organization" },
          { title: "Branch" },
          { title: "Owner" },
          { title: "Review" }
        ]}
      />
      <Form form={form} layout="vertical" requiredMark={false} initialValues={initialValues}>
        <div hidden={step !== 0}>
          <Form.Item
            label="Organization Name"
            name="organization_name"
            rules={[{ required: true, message: "Organization name is required" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="Organization Code"
            name="organization_code"
            rules={[{ required: true, message: "Organization code is required" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item label="Timezone" name="timezone" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Email" name="organization_email" rules={[{ type: "email" }]}>
            <Input />
          </Form.Item>
          <Form.Item label="Phone" name="organization_phone">
            <Input />
          </Form.Item>
        </div>
        <div hidden={step !== 1}>
          <Form.Item
            label="Branch Name"
            name="branch_name"
            rules={[{ required: true, message: "Branch name is required" }]}
          >
            <Input />
          </Form.Item>
        </div>
        <div hidden={step !== 2}>
          <Form.Item
            label="Owner Name"
            name="owner_name"
            rules={[{ required: true, message: "Owner name is required" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            label="Owner Email"
            name="owner_email"
            rules={[
              { required: true, message: "Owner email is required" },
              { type: "email", message: "Enter a valid email" }
            ]}
          >
            <Input />
          </Form.Item>
          <Form.Item label="Owner Phone" name="owner_phone">
            <Input />
          </Form.Item>
        </div>
        {step === 3 && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Organization">
              {reviewPayload.organization.name} ({reviewPayload.organization.code})
            </Descriptions.Item>
            <Descriptions.Item label="Timezone">
              {reviewPayload.organization.timezone}
            </Descriptions.Item>
            <Descriptions.Item label="Default Branch">
              {reviewPayload.branch.name}
            </Descriptions.Item>
            <Descriptions.Item label="Owner">
              {reviewPayload.owner.name} - {reviewPayload.owner.email}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Form>
      <Space>
        <Button disabled={step === 0} onClick={() => setStep((current) => current - 1)}>
          Previous
        </Button>
        {step < 3 ? (
          <Button type="primary" onClick={next}>
            Next
          </Button>
        ) : (
          <Button
            type="primary"
            icon={<CheckOutlined />}
            loading={onboardingMutation.isPending}
            onClick={submit}
          >
            Create Organization
          </Button>
        )}
      </Space>
    </Space>
  );
}

