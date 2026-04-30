import React from "react";
import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "Teacher Dashboard",
  description: "ClassLite teacher dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <h2>Teacher Dashboard</h2>
            <div className="muted">ClassLite</div>
            <nav>
              <Link href="/">Home</Link>
              <Link href="/essay-reviews">Essay Reviews</Link>
              <Link href="/question-bank">Question Bank</Link>
              <Link href="/roster">Roster</Link>
            </nav>
          </aside>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
