import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e: FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      localStorage.setItem('playerName', name.trim());
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[var(--color-canvas-light)] p-4">
      <div className="max-w-md w-full bg-[var(--color-surface-card)] p-10 rounded-lg shadow-sm border border-[var(--color-hairline-light)]">
        <div className="text-center mb-10">
          <h1 className="text-display-md text-[var(--color-primary)] font-light tracking-tight">CARO AI</h1>
          <p className="text-body-sm text-[var(--color-charcoal)] opacity-70 mt-2">
            Vui lòng nhập tên của bạn để bắt đầu
          </p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-8">
          <div>
            <label htmlFor="name" className="block text-body-sm mb-2 text-[var(--color-ink)] font-medium">
              Tên người chơi
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-md bg-[var(--color-canvas-light)] border border-[var(--color-hairline-light)] focus:outline-none focus:border-[var(--color-primary)] transition-colors text-[var(--color-ink)]"
              placeholder="Ví dụ: Keria"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-[var(--color-primary)] hover:bg-[var(--color-primary-pressed)] text-[var(--color-on-primary)] py-4 rounded-full font-medium transition-colors text-body-strong tracking-wide"
          >
            Vào Chơi
          </button>
        </form>
      </div>
    </div>
  );
}
