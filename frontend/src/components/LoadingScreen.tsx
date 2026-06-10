import { Spin } from "antd";

export function LoadingScreen() {
  return (
    <div className="loading-screen" aria-label="Loading">
      <Spin size="large" />
    </div>
  );
}
