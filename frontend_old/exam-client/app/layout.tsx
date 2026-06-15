import React from "react";
import "./globals.css";

export const metadata = {
  title: "ClassLite Formal Exam",
  description: "Secure formal exam client",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
