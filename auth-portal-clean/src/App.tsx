import { useState } from 'react';
import Starfield from './components/Starfield';
import Logo from './components/Logo';
import AuthCard from './components/AuthCard';
import Dashboard from './components/Dashboard';
import Mathbot from './components/Mathbot';
import Security from './components/Security';
import Market from './components/Market';
import PharmLab from './components/PharmLab';

export default function App() {
  const [user, setUser] = useState<string | null>(null);
  const [page, setPage] = useState('dashboard');

  return (
    <div className="relative min-h-screen bg-[#0B0A1A] overflow-hidden flex flex-col items-center justify-center font-vazirmatn">
      <Starfield />
      {!user ? (
        <div className="z-10 flex flex-col items-center w-full px-4 pt-10">
          <Logo />
          <AuthCard onLoginSuccess={(u) => { setUser(u); setPage('dashboard'); }} />
        </div>
      ) : page === 'dashboard' ? (
        <Dashboard username={user} onLogout={() => setUser(null)} onNavigate={setPage} />
      ) : page === 'mathbot' ? (
        <Mathbot onBack={() => setPage('dashboard')} />
      ) : page === 'security' ? (
        <Security onBack={() => setPage('dashboard')} />
      ) : page === 'market' ? (
        <Market onBack={() => setPage('dashboard')} />
      ) : page === 'pharmlab' ? (
        <PharmLab onBack={() => setPage('dashboard')} />
      ) : null}
    </div>
  );
}
