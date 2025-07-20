'use client';

import { useState } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { LogOut, DollarSign, Users, TrendingUp, Calendar, User, CheckCircle } from 'lucide-react';

interface FinancialData {
  age: string;
  income: string;
  dependents: string;
  riskTolerance: string;
}

interface RecommendedPlan {
  plan_id: number;
  plan_name: string;
  plan_type: string;
  sum_assured_range: string;
  description: string;
  match_score: number;
}

interface ApiResponse {
  success: boolean;
  message: string;
  data: {
    history: {
      id: number;
      created_at: string;
    };
    recommended_plans: RecommendedPlan[];
  };
  timestamp: string;
}

export default function HomePage() {
  const { user, logout } = useAuth();
  const [formData, setFormData] = useState<FinancialData>({
    age: '',
    income: '',
    dependents: '',
    riskTolerance: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.age || !formData.income || !formData.dependents || !formData.riskTolerance) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const userData = localStorage.getItem('user');
      if (!userData) {
        throw new Error('User not found in localStorage');
      }

      const user = JSON.parse(userData);
      const userId = user.user_id;

      // Prepare the API request data
      const requestData = {
        user_id: userId,
        age: parseInt(formData.age),
        annual_income: parseInt(formData.income),
        no_of_dependent: parseInt(formData.dependents),
        risk_capacity: formData.riskTolerance.toLowerCase()
      };

      console.log("Submitting data:", requestData);

      // Call the API
      const response = await fetch('http://localhost:8000/save-user-history/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Failed to save data');
      }

      // Save to localStorage as fallback
      localStorage.setItem(`financial_data_${userId}`, JSON.stringify(formData));
      setApiResponse(result);
      setIsSubmitted(true);
      toast.success('Financial information saved successfully!');
      
    } catch (error) {
      console.error('Error saving data:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to save financial information');
    }
  };

  const handleInputChange = (field: keyof FinancialData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50">
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-sm border-b shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-semibold text-gray-900">Welcome back, {user?.name}</h1>
                <p className="text-sm text-gray-600">{user?.email}</p>
              </div>
            </div>
            <Button variant="outline" onClick={handleLogout} className="flex items-center space-x-2">
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </Button>
          </div>
        </header>

        <div className="max-w-7xl mx-auto p-4 py-8 space-y-8">
          <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div className="space-y-1 mb-4 md:mb-0">
                  <h2 className="text-xl font-bold text-gray-900">Financial Profile Summary</h2>
                  <p className="text-gray-600">Here's your financial information and recommended plans</p>
                </div>
                <Button 
                  onClick={() => setIsSubmitted(false)}
                  variant="outline"
                  className="w-full md:w-auto"
                >
                  Edit Information
                </Button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Age</p>
                  <p className="font-semibold">{formData.age} years</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Annual Income</p>
                  <p className="font-semibold">₹{parseInt(formData.income).toLocaleString()}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Dependents</p>
                  <p className="font-semibold">{formData.dependents}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-500">Risk Tolerance</p>
                  <p className={`font-medium capitalize ${
                    formData.riskTolerance === 'low' ? 'text-red-600' :
                    formData.riskTolerance === 'medium' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {formData.riskTolerance}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Recommended Insurance Plans</h2>
              <p className="text-sm text-gray-500">
                {apiResponse?.data?.recommended_plans?.length || 0} plans matched
              </p>
            </div>

            {apiResponse?.data?.recommended_plans?.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {apiResponse.data.recommended_plans.map((plan) => (
                  <Card key={plan.plan_id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{plan.plan_name}</CardTitle>
                          <CardDescription className="capitalize">
                            {plan.plan_type.replace('_', ' ')} plan
                          </CardDescription>
                        </div>
                        <div className="px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-medium">
                          {(plan.match_score * 100).toFixed(0)}% match
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">Sum Assured</span>
                        <span className="font-medium">₹{plan.sum_assured_range}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">Plan Type</span>
                        <span className="font-medium capitalize">
                          {plan.plan_type.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="pt-2">
                        <p className="text-sm text-gray-600">{plan.description}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="text-center py-12">
                <CardContent>
                  <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-8 w-8 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-1">No plans found</h3>
                  <p className="text-gray-500">
                    We couldn't find any plans matching your profile. Try adjusting your criteria.
                  </p>
                  <Button
                    onClick={() => setIsSubmitted(false)}
                    variant="outline"
                    className="mt-4"
                  >
                    Adjust Profile
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-emerald-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-900">Welcome back, {user?.name}</h1>
              <p className="text-sm text-gray-600">{user?.email}</p>
            </div>
          </div>
          <Button variant="outline" onClick={handleLogout} className="flex items-center space-x-2">
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </Button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-4 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Financial Assessment</h2>
          <p className="text-gray-600">Help us understand your financial situation to provide personalized recommendations</p>
        </div>

        <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-semibold flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <span>Your Financial Profile</span>
            </CardTitle>
            <CardDescription>
              Please provide the following information to help us create your investment strategy
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="age" className="text-sm font-medium flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-blue-600" />
                    <span>Age</span>
                  </Label>
                  <Input
                    id="age"
                    type="number"
                    placeholder="Enter your age"
                    value={formData.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    className="h-11"
                    min="18"
                    max="100"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="income" className="text-sm font-medium flex items-center space-x-2">
                    <DollarSign className="w-4 h-4 text-green-600" />
                    <span>Annual Income</span>
                  </Label>
                  <Input
                    id="income"
                    type="number"
                    placeholder="Enter your annual income"
                    value={formData.income}
                    onChange={(e) => handleInputChange('income', e.target.value)}
                    className="h-11"
                    min="0"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="dependents" className="text-sm font-medium flex items-center space-x-2">
                    <Users className="w-4 h-4 text-purple-600" />
                    <span>Number of Dependents</span>
                  </Label>
                  <Input
                    id="dependents"
                    type="number"
                    placeholder="Number of dependents"
                    value={formData.dependents}
                    onChange={(e) => handleInputChange('dependents', e.target.value)}
                    className="h-11"
                    min="0"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-sm font-medium flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-orange-600" />
                    <span>Risk Tolerance</span>
                  </Label>
                  <Select value={formData.riskTolerance} onValueChange={(value) => handleInputChange('riskTolerance', value)}>
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder="Select your risk tolerance" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span>Low - Conservative investments</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="medium">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                          <span>Medium - Balanced approach</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="high">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span>High - Aggressive growth</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="pt-4">
                <Button 
                  type="submit" 
                  className="w-full h-12 bg-blue-600 hover:bg-blue-700 transition-colors text-base"
                >
                  Submit Financial Information
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}