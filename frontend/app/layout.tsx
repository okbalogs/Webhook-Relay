import "./globals.css";
import React from "react";

export const metadata = {
  title: "Webhook Relay & Replay Platform",
  description: "Self-hosted Developer Webhook Broker & Inspection Tool",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-dark-900 text-gray-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}

