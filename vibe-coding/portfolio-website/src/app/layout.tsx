import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alex Rivera — Data Scientist & Engineer",
  description: "Portfolio website for Alex Rivera, Data Scientist and Data Engineer",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
