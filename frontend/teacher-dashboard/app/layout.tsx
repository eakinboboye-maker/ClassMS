import React from "react";
import "./globals.css";

export const metadata = {
  title: "ClassLite Teacher Dashboard",
  description: "Teacher dashboard for ClassLite",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
