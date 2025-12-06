import React from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../../context/authContext';
// Placeholder imports for ShadCN components:
// import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
// import { Input } from '@/components/ui/input';
// import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast'; 

// Define the validation schema
const formSchema = z.object({
  email: z.string().email("Invalid email format."),
  password: z.string().min(1, "Password is required."),
});

const LoginForm = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast(); // Placeholder for ShadCN toast

  // 1. Initialize the form
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });
  
  const { isSubmitting } = form.formState;

  // 2. Handle Form Submission
  const onSubmit = async (values) => {
    try {
      // Call the context function to handle API login
      const result = await login(values.email, values.password);

      // toast({ title: "Success", description: "Login successful!" });
      console.log("Login successful! User:", result.user);

      // 3. Redirect based on role
      const userRole = result.user.role.toLowerCase();
      
      if (userRole === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/applicant', { replace: true });
      }

    } catch (error) {
      // Handle API errors (e.g., 401 Unauthorized from Django)
      const errorMessage = error.response?.data?.detail || "Login failed. Check your email and password.";
      toast({ title: "Error", description: errorMessage, variant: "destructive" });
      console.error("Login failed:", errorMessage);
      form.resetField('password'); // Clear password field on failure
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      {/* ⚠️ NOTE: Replace the divs with actual ShadCN <Form>, <FormField>, <Input>, and <Button> components */}

      {/* Email Field */}
      <div className="space-y-2">
        <label htmlFor="email">Email Address</label>
        <input 
          id="email" 
          {...form.register("email")} 
          disabled={isSubmitting} 
          className="w-full border p-2 rounded" 
        />
        {form.formState.errors.email && <p className="text-red-500 text-sm">{form.formState.errors.email.message}</p>}
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
        className="w-full py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
      >
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

export default LoginForm;