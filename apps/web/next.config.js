/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    // API URL - defaults to localhost:8000
    // Can be set via NEXT_PUBLIC_API_URL environment variable
    // Or via infra/.env (not loaded here, but can be set manually)
    API_URL: process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig

