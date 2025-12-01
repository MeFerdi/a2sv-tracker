import { useAuth } from './AuthContext';
import { Button } from '@/components/ui/button';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold">A2SV Tracker</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            {isAuthenticated() ? (
              <>
                <span className="text-sm text-muted-foreground">
                  {user?.email || user?.username || 'User'}
                </span>
                <Button variant="outline" onClick={logout}>
                  Logout
                </Button>
              </>
            ) : (
              <Button variant="default" asChild>
                <a href="/login">Login</a>
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
};

