import type { Metadata, Viewport } from 'next';
import { AuthProvider } from '@/lib/contexts/AuthContext';
import './globals.css';

export const metadata: Metadata = {
  title: 'Dental Practice Management',
  description: 'iPad-optimized dental practice management application',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Dental Practice',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
