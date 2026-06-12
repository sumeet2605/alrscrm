import { ArrowLeftOutlined, LockOutlined, SaveOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Form, Input, Space, Typography } from "antd";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import type { ChangePasswordRequest } from "../types/auth";

interface ChangePasswordFormValues extends ChangePasswordRequest {
  confirm_password: string;
}

const passwordRules = [
  { required: true, message: "New password is required" },
  { min: 8, message: "Use at least 8 characters" },
  {
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
    message: "Use uppercase, lowercase, and a number"
  }
];

export function ChangePasswordPage() {
  const { changePassword, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const from = (location.state as { from?: Location } | null)?.from?.pathname ?? "/dashboard";

  const handleSubmit = async (values: ChangePasswordFormValues) => {
    setError(null);
    setIsSubmitting(true);
    try {
      await changePassword({
        current_password: values.current_password,
        new_password: values.new_password
      });
      navigate(from === "/change-password" ? "/dashboard" : from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Password change failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="auth-task-page">
      <Card className="auth-task-card">
        <Space direction="vertical" size={16} className="page-stack">
          <div className="page-heading">
            <div>
              <Typography.Title level={2}>Change Password</Typography.Title>
              <Typography.Text type="secondary">{user?.email}</Typography.Text>
            </div>
            {!user?.password_reset_required ? (
              <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/dashboard")}>
                Back
              </Button>
            ) : null}
          </div>
          {user?.password_reset_required ? (
            <Alert type="warning" showIcon message="Password change required" />
          ) : null}
          {error ? <Alert type="error" showIcon message={error} /> : null}
          <Form<ChangePasswordFormValues>
            layout="vertical"
            requiredMark={false}
            onFinish={handleSubmit}
          >
            <Form.Item
              label="Current Password"
              name="current_password"
              rules={[{ required: true, message: "Current password is required" }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                autoComplete="current-password"
                size="large"
              />
            </Form.Item>
            <Form.Item label="New Password" name="new_password" rules={passwordRules}>
              <Input.Password prefix={<LockOutlined />} autoComplete="new-password" size="large" />
            </Form.Item>
            <Form.Item
              label="Confirm Password"
              name="confirm_password"
              dependencies={["new_password"]}
              rules={[
                { required: true, message: "Confirm the new password" },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue("new_password") === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error("Passwords do not match"));
                  }
                })
              ]}
            >
              <Input.Password prefix={<LockOutlined />} autoComplete="new-password" size="large" />
            </Form.Item>
            <div className="form-actions">
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={isSubmitting}
              >
                Save Password
              </Button>
            </div>
          </Form>
        </Space>
      </Card>
    </main>
  );
}
