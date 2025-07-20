'use client';

import { useEffect, useState } from 'react';
import { useAuth } from './AuthProvider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Mail, Lock, ArrowRight, Shield } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const { login, verifyOtp, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    console.log("Current step:", step);
    console.log("Current email:", email);
  }, [step, email]);

  // Manual OTP verification trigger
  const showOtpSection = () => {
    setStep('otp');
    // setEmail('demo@example.com');
    toast.info('Showing OTP verification section');
  };

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    try {
      const { success, pendingEmail } = await login(email);
      console.log("Login response:", { success, pendingEmail });

      if (success) {
        setStep('otp');
        setEmail(pendingEmail || email);
        toast.success('OTP sent to your email address');
      }
    } catch (error) {
      toast.error('Failed to send OTP');
      console.error("Login error:", error);
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otp) {
      toast.error('Please enter the OTP');
      return;
    }

    const response = await verifyOtp(otp);
    if (response?.success === true) {
      toast.success('Login successful!');
      router.push('/');
    } else {
      toast.error('Invalid OTP. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2 relative">
          <div className="flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mx-auto mb-4">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">SafeCheck</h1>
          <p className="text-gray-600">Secure access to your financial planning</p>
          
          {/* Manual OTP trigger button (visible in development) */}
          {process.env.NODE_ENV === 'development' && (
            <button
              onClick={showOtpSection}
              className="absolute right-0 top-0 text-xs text-gray-500 underline"
            >
              [DEV] Show OTP
            </button>
          )}
        </div>

        <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
          <CardHeader className="space-y-1 pb-4">
            <CardTitle className="text-2xl font-semibold text-center">
              {step === 'email' ? 'Welcome Back' : 'Verify Your Identity'}
            </CardTitle>
            <CardDescription className="text-center text-gray-600">
              {step === 'email' 
                ? 'Enter your email to receive an OTP' 
                : 'Enter the 6-digit code sent to your email'
              }
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-4">
            {step === 'email' ? (
              <form onSubmit={handleEmailSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 h-11"
                      disabled={isLoading}
                    />
                  </div>
                </div>
                
                <Button 
                  type="submit" 
                  className="w-full h-11 bg-blue-600 hover:bg-blue-700 transition-colors"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Sending OTP...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <span>Send OTP</span>
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  )}
                </Button>
              </form>
            ) : (
              <form onSubmit={handleOtpSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="otp" className="text-sm font-medium">Verification Code</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      id="otp"
                      type="text"
                      placeholder="Enter 6-digit code"
                      value={otp}
                      onChange={(e) => setOtp(e.target.value)}
                      className="pl-10 h-11 tracking-widest"
                      maxLength={6}
                      disabled={isLoading}
                    />
                  </div>
                  <p className="text-xs text-gray-500">
                    Code sent to {email}
                  </p>
                </div>
                
                <div className="space-y-3">
                  <Button 
                    type="submit" 
                    className="w-full h-11 bg-blue-600 hover:bg-blue-700 transition-colors"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Verifying...</span>
                      </div>
                    ) : (
                      'Verify & Login'
                    )}
                  </Button>
                  
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="w-full h-11"
                    onClick={() => setStep('email')}
                    disabled={isLoading}
                  >
                    Back to Email
                  </Button>
                </div>
              </form>
            )}
            
            <div className="text-center pt-4 border-t">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link href="/signup" className="text-blue-600 hover:text-blue-700 font-medium transition-colors">
                  Sign up here
                </Link>
              </p>
            </div>

            {step === 'otp' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}