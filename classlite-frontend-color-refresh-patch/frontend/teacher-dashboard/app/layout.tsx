import React from "react";
import "./globals.css";

export const metadata = {
  title: "ClassLite Teacher Dashboard",
  description: "Teacher dashboard for class management, rosters, questions, and reviews",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <nav className="topnav">
          <div className="topnav-inner">
            <a className="brand" href="/">ClassLite</a>
            <a href="/">Home</a>
            <a href="/essay-reviews">Essay Reviews</a>
            <a href="/question-bank">Question Bank</a>
            <a href="/roster">Roster</a>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
