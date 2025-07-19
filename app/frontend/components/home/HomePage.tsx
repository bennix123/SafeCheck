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

export default function HomePage() {
  const { user, logout } = useAuth();
  const [formData, setFormData] = useState<FinancialData>({
    age: '',
    income: '',
    dependents: '',
    riskTolerance: ''
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.age || !formData.income || !formData.dependents || !formData.riskTolerance) {
      toast.error('Please fill in all fields');
      return;
    }

    // Save the financial data
    localStorage.setItem(`financial_data_${user?.id}`, JSON.stringify(formData));
    setIsSubmitted(true);
    toast.success('Financial information saved successfully!');
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
          <Card className="border-0 shadow-xl bg-white/80 backdrop-blur-sm">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Financial Profile Complete!</h2>
              <p className="text-gray-600 mb-6">
                Thank you for providing your financial information. Our team will analyze your profile and provide personalized investment recommendations.
              </p>
              
              <div className="bg-gray-50 rounded-lg p-6 space-y-4 text-left max-w-md mx-auto">
                <h3 className="font-semibold text-gray-900 mb-4">Your Information:</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Age:</span>
                    <span className="font-medium">{formData.age} years</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Annual Income:</span>
                    <span className="font-medium">${parseInt(formData.income).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Dependents:</span>
                    <span className="font-medium">{formData.dependents}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Risk Tolerance:</span>
                    <span className={`font-medium capitalize px-2 py-1 rounded text-xs ${
                      formData.riskTolerance === 'low' ? 'bg-red-100 text-red-700' :
                      formData.riskTolerance === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {formData.riskTolerance}
                    </span>
                  </div>
                </div>
              </div>

              <Button 
                onClick={() => setIsSubmitted(false)}
                variant="outline"
                className="mt-6"
              >
                Edit Information
              </Button>
            </CardContent>
          </Card>
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