"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { authService } from "@/lib/authService";

interface User {
  id: string;
  name: string;
  email: string;
  dateOfBirth: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string) => Promise<boolean>;
  verifyOtp: (otp: string) => Promise<boolean>;
  signup: (data: {
    name: string;
    email: string;
    dateOfBirth: string;
  }) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pendingEmail, setPendingEmail] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check for existing session
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (
  email: string
): Promise<{ 
  success: boolean; 
  pendingEmail?: string; 
  message?: string 
}> => {
  setIsLoading(true);
  setError(null);

  try {
    const result =await authService.sendOtp(email);
    console.log(result,"---result")
    if (!result.success) {
      console.log("i am here")
      const errorMessage = result.message || "Failed to send OTP";
      setError(errorMessage);
      return { success: false, message: errorMessage };
    }
   const message = "success";
    setPendingEmail(email);
    return { success: true, pendingEmail: email,message };
  } catch (err) {
    const message = err instanceof Error ? err.message : "Login failed";
    setError(message);
    return { success: false, message };
  } finally {
    setIsLoading(false);
  }
};

  const verifyOtp = async (
    otp: string
  ): Promise<{
    success: boolean;
    message?: string;
    user?: User;
  }> => {
    setIsLoading(true);
    try {
      const result = await authService.verifyOtp(pendingEmail,otp)

      if (!result.success) {
        throw new Error(result.message || "Invalid OTP");
      }
      // Only set user after successful verification
      setUser(result.data);
      localStorage.setItem("user", JSON.stringify(result.data));
      setPendingEmail("");
      return { success: true, user: result.data };
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "OTP verification failed";
      setError(message);
      return { success: false, message };
    } finally {
      setIsLoading(false);
    }
  };
  const signup = async (data: {
    name: string;
    email: string;
    dateOfBirth: string;
  }): Promise<{
    success: boolean;
    message?: string;
    user?: User;
  }> => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.signup(data);
      if (!result.success) {
        console.error("Signup failed:", result.message);
        throw new Error(result.message || "Signup failed");
      }
      return { success: true, user: result.data };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Signup failed";
      setError(message);
      return { success: false, message };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
    setPendingEmail("");
  };

  return (
    <AuthContext.Provider
      value={{ user, login, verifyOtp, signup, logout, isLoading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
