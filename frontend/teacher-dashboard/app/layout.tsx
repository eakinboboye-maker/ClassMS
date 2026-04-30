import React from "react";
import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "Teacher Dashboard",
  description: "Class management teacher dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "Arial, sans-serif", margin: 0, background: "#f7f7f7" }}>
        <div style={{ display: "flex", minHeight: "100vh" }}>
          <aside
            style={{
              width: 240,
              padding: 16,
              background: "#fff",
              borderRight: "1px solid #ddd",
            }}
          >
            <h2>Teacher Dashboard</h2>

            <nav style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <Link href="/">Home</Link>
              <Link href="/essay-reviews">Essay Reviews</Link>
              <Link href="/question-bank">Question Bank</Link>
              <Link href="/roster">Roster</Link>
            </nav>
          </aside>

          <main style={{ flex: 1, padding: 24 }}>{children}</main>
        </div>
      </body>
    </html>
  );
}
