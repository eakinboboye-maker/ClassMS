import React from "react";

export const metadata = {
  title: "Formal Exam Client",
  description: "SEB-backed formal exam client",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "Arial, sans-serif", margin: 0, background: "#f5f5f5" }}>
        {children}
      </body>
    </html>
  );
}
