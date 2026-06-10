import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Form, Input, Typography } from "antd";
import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import type { LoginRequest } from "../types/auth";

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: Location } | null)?.from?.pathname ?? "/dashboard";

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (values: LoginRequest) => {
    setError(null);
    setIsSubmitting(true);
    try {
      await login(values);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-panel">
        <div className="login-copy">
          <Typography.Title level={1}>ALRSCRM</Typography.Title>
          <Typography.Paragraph>
            A premium operating system for high-touch photography studios.
          </Typography.Paragraph>
        </div>
        <Card className="login-card">
          <Typography.Title level={3}>Sign in</Typography.Title>
          <Typography.Text type="secondary">Use your studio account to continue.</Typography.Text>
          {error ? <Alert className="form-alert" type="error" message={error} showIcon /> : null}
          <Form<LoginRequest> layout="vertical" onFinish={handleSubmit} requiredMark={false}>
            <Form.Item
              label="Email"
              name="email"
              rules={[
                { required: true, message: "Email is required" },
                { type: "email", message: "Enter a valid email" }
              ]}
            >
              <Input prefix={<MailOutlined />} size="large" autoComplete="email" />
            </Form.Item>
            <Form.Item
              label="Password"
              name="password"
              rules={[{ required: true, message: "Password is required" }]}
            >
              <Input.Password prefix={<LockOutlined />} size="large" autoComplete="current-password" />
            </Form.Item>
            <Button block size="large" type="primary" htmlType="submit" loading={isSubmitting}>
              Sign in
            </Button>
          </Form>
        </Card>
      </section>
    </main>
  );
}
