import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'VoteGuard Nexus',
  description: 'VoteGuard Nexus frontend scaffold',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
