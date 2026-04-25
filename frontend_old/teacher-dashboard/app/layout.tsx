import React from "react";

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
        {children}
      </body>
    </html>
  );
}
