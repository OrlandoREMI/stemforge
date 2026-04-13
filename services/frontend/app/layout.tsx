import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "stemforge",
  description: "Self-hosted YouTube to stems separation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
