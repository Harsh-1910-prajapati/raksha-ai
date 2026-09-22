import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/react";
import "./globals.css";

export const metadata: Metadata = {
  title: "RakshaAI — AI-Powered Pre-Disaster Intelligence",
  description:
    "RakshaAI helps disaster-management teams understand what could be affected BEFORE a disaster: scenario simulation, transparent risk index, critical infrastructure exposure, Gemini AI reasoning, emergency action plans and multilingual alerts.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-slate-100">
        {children}
        <Analytics />
      </body>
    </html>
  );
}