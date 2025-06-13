import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // TODO: Add the Production Domain
  images: {
    domains: ["760b-154-177-34-214.ngrok-free.app"],
  },
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    }
  }
};

export default nextConfig;
