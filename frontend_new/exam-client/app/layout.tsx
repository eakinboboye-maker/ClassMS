import React from "react";
import "./globals.css";

export const metadata = {
  title: "Exam Client",
  description: "ClassLite formal exam client",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
