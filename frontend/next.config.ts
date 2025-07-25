import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // TODO: Add the Production Domain
  images: {
    domains: ["aba6-154-182-238-185.ngrok-free.app"],
  },
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    }
  }
};

export default nextConfig;
