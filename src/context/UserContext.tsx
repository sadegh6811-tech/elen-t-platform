import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';

interface UserContextType {
  user: User | null;
  isLoggedIn: boolean;
  role: UserRole;
  login: () => void;
  logout: () => void;
  setRole: (role: UserRole) => void;
  toggleRole: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

const ROLE_STORAGE_KEY = 'elen_user_role';

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRoleState] = useState<UserRole>(() => {
    try {
      const stored = localStorage.getItem(ROLE_STORAGE_KEY) as UserRole;
      if (stored === 'platform_admin' || stored === 'technician') {
        return stored;
      }
    } catch {
      // fallback
    }
    return 'technician';
  });

  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(true);

  const [user, setUser] = useState<User | null>({
    id: 'tech-001',
    name: 'کاظمی',
    email: 'kazemi@elen.ir',
    role: role
  });

  useEffect(() => {
    if (isLoggedIn) {
      setUser({
        id: 'tech-001',
        name: 'کاظمی',
        email: 'kazemi@elen.ir',
        role: role
      });
    } else {
      setUser(null);
    }
  }, [role, isLoggedIn]);

  const setRole = (newRole: UserRole) => {
    try {
      localStorage.setItem(ROLE_STORAGE_KEY, newRole);
    } catch {
      // ignore
    }
    setRoleState(newRole);
  };

  const toggleRole = () => {
    const next = role === 'platform_admin' ? 'technician' : 'platform_admin';
    setRole(next);
  };

  const login = () => {
    setIsLoggedIn(true);
  };

  const logout = () => {
    setIsLoggedIn(false);
  };

  return (
    <UserContext.Provider
      value={{
        user,
        isLoggedIn,
        role,
        login,
        logout,
        setRole,
        toggleRole
      }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
