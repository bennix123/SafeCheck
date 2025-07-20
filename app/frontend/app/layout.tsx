import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from 'sonner';
import { AuthProvider } from '@/components/auth/AuthProvider';
import { Suspense } from 'react';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'SafeCheck - Secure Financial Planning',
  description: 'Secure authentication and financial planning application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return ( 
    <html lang="en">
      <body className={inter.className}>
        <Suspense fallback={<div>Loading...</div>}>
          <AuthProvider>
            {children}
          </AuthProvider>
        </Suspense>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}