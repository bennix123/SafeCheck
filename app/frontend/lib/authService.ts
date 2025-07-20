"use client";

import axios, { AxiosError, AxiosResponse } from 'axios';

interface User {
    id: string;
    name: string;
    email: string;
    dateOfBirth: string;
}

interface ApiResponse<T = any> {
    success: boolean;
    message?: string;
    data?: T;
}

interface OtpResponse {
    success: boolean;
    message?: string;
}

interface VerifyOtpResponse {
    success: boolean;
    message?: string;
    user?: User;
}

interface SignupResponse {
    success: boolean;
    message?: string;
    user?: User;
}

interface UserHistoryRequest {
    userId: string;
    action: string;
    details: Record<string, any>;
}

interface UserHistoryResponse {
    success: boolean;
    message?: string;
    data?: {
        id: string;
        timestamp: string;
    };
}

class AuthService {
    private baseUrl: string;
    private axiosInstance;

    constructor() {
        this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

        this.axiosInstance = axios.create({
            baseURL: this.baseUrl,
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: 10000,
        });
    }

    /**
     * Send OTP to user's email for login
     */
    async sendOtp(email: string): Promise<ApiResponse<OtpResponse>> {
        try {
            const response = await this.axiosInstance.post('/send-otp/', { email });
            return response.data;
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Verify OTP for user login
     */
    async verifyOtp(email: string, otp: string): Promise<ApiResponse<VerifyOtpResponse>> {
        try {
            const response = await this.axiosInstance.post('/verify-otp/', { email, otp });
            return response.data;
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Register a new user
     */
    async signup(userData: {
        name: string;
        email: string;
        dateOfBirth: string;
    }): Promise<ApiResponse<SignupResponse>> {
        try {
            const response = await this.axiosInstance.post('/signup/', userData);
            return response.data;
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Save user history
     */
    async saveUserHistory(requestData: UserHistoryRequest): Promise<ApiResponse<UserHistoryResponse>> {
        try {
            const response = await this.axiosInstance.post('/save-user-history/', requestData);
            return response.data;
        } catch (error) {
            return this.handleError(error);
        }
    }

    /**
     * Common error handler
     */
    private handleError(error: unknown): ApiResponse {
        if (axios.isAxiosError(error)) {
            return {
                success: false,
                message: error.response?.data?.message ||
                    error.message ||
                    'Network error occurred'
            };
        }

        return {
            success: false,
            message: 'An unexpected error occurred'
        };
    }
}
export const authService = new AuthService();