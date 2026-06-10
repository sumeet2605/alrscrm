import { Alert, Button, Result } from "antd";
import { Component, type ErrorInfo, type ReactNode } from "react";

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Frontend error boundary", error, info);
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <Result
        status="500"
        title="Something went wrong"
        subTitle="The application could not render this view."
        extra={[
          <Button key="reload" type="primary" onClick={() => window.location.reload()}>
            Reload
          </Button>,
          this.state.error ? (
            <Alert key="message" type="error" message={this.state.error.message} showIcon />
          ) : null
        ]}
      />
    );
  }
}
