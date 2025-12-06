import React from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../../context/AuthContext';
// Assuming these ShadCN components are available:
// import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
// import { Input } from '@/components/ui/input';
// import { Button } from '@/components/ui/button';
// import { useToast } from '@/components/ui/use-toast'; 

// Define the validation schema using Zod
const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters."),
  password: z.string().min(6, "Password must be at least 6 characters."),
  // The token is read from the URL, but we'll include it in the form data structure
});

const TokenRegisterForm = () => {
  const { registerWithToken } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  // const { toast } = useToast(); // Placeholder for ShadCN toast

  // 1. Initialize the form
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      password: "",
    },
  });
  
  const { isSubmitting } = form.formState;

  // 2. Handle Form Submission
  const onSubmit = async (values) => {
    if (!token) {
      // toast({ title: "Error", description: "Registration token is missing.", variant: "destructive" });
      console.error("Registration token is missing.");
      return;
    }

    try {
      // Call the context function
      const result = await registerWithToken(token, values.name, values.password);

      // toast({ title: "Success", description: "Account created successfully!" });
      console.log("Registration successful! User:", result.user);

      // 3. Redirect based on role (Case-insensitive match for security)
      const userRole = result.user.role.toLowerCase();
      
      if (userRole === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/applicant', { replace: true });
      }

    } catch (error) {
      // Handle API errors and display feedback
      const errorMessage = error.response?.data?.detail || "Registration failed. Please check your inputs or the token might be expired.";
      // toast({ title: "Error", description: errorMessage, variant: "destructive" });
      console.error("Registration failed:", errorMessage);
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      {/* ⚠️ NOTE: Replace the divs with actual ShadCN <Form>, <FormField>, <Input>, and <Button> components */}

      {/* Name Field */}
      <div className="space-y-2">
        <label htmlFor="name">Full Name</label>
        <input 
          id="name" 
          {...form.register("name")} 
          disabled={isSubmitting} 
          className="w-full border p-2 rounded" 
        />
        {form.formState.errors.name && <p className="text-red-500 text-sm">{form.formState.errors.name.message}</p>}
      </div>

      {/* Password Field */}
      <div className="space-y-2">
        <label htmlFor="password">Password</label>
        <input 
          id="password" 
          type="password" 
          {...form.register("password")} 
          disabled={isSubmitting} 
          className="w-full border p-2 rounded" 
        />
        {form.formState.errors.password && <p className="text-red-500 text-sm">{form.formState.errors.password.message}</p>}
      </div>

      <button 
        type="submit" 
        disabled={isSubmitting} 
        className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? 'Registering...' : 'Set Password and Register'}
      </button>

      {!token && (
        <p className="text-center text-red-500 mt-4">Error: Missing registration token in URL.</p>
      )}
    </form>
  );
};

export default TokenRegisterForm;