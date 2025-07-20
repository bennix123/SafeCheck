"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

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
    const response = await fetch("http://localhost:8000/send-otp/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const result = await response.json();
    console.log(result,"---result")

    if (result.success===false) {
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
      const response = await fetch("http://localhost:8000/verify-otp/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: pendingEmail,
          otp,
        }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
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

  // const verifyOtp = async (otp: string): Promise<boolean> => {
  //   setIsLoading(true);
  //   // Simulate API call
  //   await new Promise(resolve => setTimeout(resolve, 1000));

  //   // Simple OTP verification (in real app, this would be server-side)
  //   if (otp === '123456') {
  //     const users = JSON.parse(localStorage.getItem('users') || '[]');
  //     const userData = users.find((u: User) => u.email === pendingEmail);

  //     if (userData) {
  //       setUser(userData);
  //       localStorage.setItem('user', JSON.stringify(userData));
  //       setPendingEmail('');
  //       setIsLoading(false);
  //       return true;
  //     }
  //   }

  //   setIsLoading(false);
  //   return false;
  // };

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
      const response = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      console.log("Signup Response:", result);
      console.log("Signup Data:", result.success);

      if (!result.success) {
        console.error("Signup failed:", result.message);
        throw new Error(result.message || "Signup failed");
      }

      // setUser(result.data);
      // localStorage.setItem("user", JSON.stringify(result.data));
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
