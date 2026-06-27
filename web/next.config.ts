import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Proxy API calls to the FastAPI backend during local dev so the frontend
  // can hit the real `/api/v1/detect/*` contract without CORS friction.
  async rewrites() {
    const backend = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
    return [{ source: "/api/v1/:path*", destination: `${backend}/api/v1/:path*` }];
  },
};

export default nextConfig;
