import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, RefreshCw, Trophy, User, Bot } from 'lucide-react';
import { getAIMove, type Difficulty } from '../lib/api';

const GRID_SIZE = 15;
const PLAYER_VAL = 1; // X
const AI_VAL = 2; // O

const checkWin = (grid: number[][], player: number) => {
  const size = GRID_SIZE;
  for (let r = 0; r < size; r++) {
    for (let c = 0; c <= size - 5; c++) {
      if (grid[r][c] === player && grid[r][c+1] === player && grid[r][c+2] === player && grid[r][c+3] === player && grid[r][c+4] === player) return true;
    }
  }
  for (let r = 0; r <= size - 5; r++) {
    for (let c = 0; c < size; c++) {
      if (grid[r][c] === player && grid[r+1][c] === player && grid[r+2][c] === player && grid[r+3][c] === player && grid[r+4][c] === player) return true;
    }
  }
  for (let r = 0; r <= size - 5; r++) {
    for (let c = 0; c <= size - 5; c++) {
      if (grid[r][c] === player && grid[r+1][c+1] === player && grid[r+2][c+2] === player && grid[r+3][c+3] === player && grid[r+4][c+4] === player) return true;
    }
  }
  for (let r = 4; r < size; r++) {
    for (let c = 0; c <= size - 5; c++) {
      if (grid[r][c] === player && grid[r-1][c+1] === player && grid[r-2][c+2] === player && grid[r-3][c+3] === player && grid[r-4][c+4] === player) return true;
    }
  }
  return false;
};

const isBoardFull = (grid: number[][]) => {
  return grid.every(row => row.every(cell => cell !== 0));
};

export default function Game() {
  const navigate = useNavigate();
  const [playerName, setPlayerName] = useState<string>('');
  const [grid, setGrid] = useState<number[][]>(Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0)));
  const [difficulty, setDifficulty] = useState<Difficulty>('medium');
  const [turn, setTurn] = useState<number>(PLAYER_VAL);
  const [winner, setWinner] = useState<number | null>(null);
  const [isAiThinking, setIsAiThinking] = useState(false);

  useEffect(() => {
    const name = localStorage.getItem('playerName');
    if (!name) {
      navigate('/login');
    } else {
      setPlayerName(name);
    }
  }, [navigate]);

  const handleCellClick = async (r: number, c: number) => {
    if (winner !== null || grid[r][c] !== 0 || turn !== PLAYER_VAL || isAiThinking) return;

    // Player move
    const newGrid = grid.map(row => [...row]);
    newGrid[r][c] = PLAYER_VAL;
    setGrid(newGrid);

    if (checkWin(newGrid, PLAYER_VAL)) {
      setWinner(PLAYER_VAL);
      return;
    }
    if (isBoardFull(newGrid)) {
      setWinner(0); // Draw
      return;
    }

    setTurn(AI_VAL);
    setIsAiThinking(true);

    try {
      const move = await getAIMove(newGrid, difficulty, AI_VAL, PLAYER_VAL);
      if (move.r !== -1 && move.c !== -1) {
        newGrid[move.r][move.c] = AI_VAL;
        setGrid([...newGrid]);
        
        if (checkWin(newGrid, AI_VAL)) {
          setWinner(AI_VAL);
        } else if (isBoardFull(newGrid)) {
          setWinner(0);
        } else {
          setTurn(PLAYER_VAL);
        }
      }
    } catch (error) {
      console.error('Failed to get AI move:', error);
      alert('Lỗi kết nối với máy chủ AI.');
      setTurn(PLAYER_VAL); // Reset turn
    } finally {
      setIsAiThinking(false);
    }
  };

  const handleRestart = () => {
    setGrid(Array(GRID_SIZE).fill(null).map(() => Array(GRID_SIZE).fill(0)));
    setWinner(null);
    setTurn(PLAYER_VAL);
  };

  const handleLogout = () => {
    localStorage.removeItem('playerName');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[var(--color-surface-soft)] flex flex-col font-sans">
      <header className="bg-[var(--color-canvas-light)] border-b border-[var(--color-hairline-light)] p-4 flex justify-between items-center shadow-sm">
        <h1 className="text-heading-lg text-[var(--color-primary)] font-light tracking-tight">CARO AI</h1>
        <div className="flex items-center gap-4">
          <span className="text-body-sm text-[var(--color-charcoal)] font-medium flex items-center gap-2">
            <User size={16} /> {playerName}
          </span>
          <button onClick={handleLogout} className="text-[var(--color-ink)] hover:text-[var(--color-primary)] transition-colors p-2 rounded-full hover:bg-[var(--color-surface-soft)]" title="Đăng xuất">
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <main className="flex-1 flex flex-col md:flex-row items-start justify-center gap-8 p-4 md:p-8">
        
        {/* Control Panel */}
        <div className="w-full md:w-72 bg-[var(--color-canvas-light)] rounded-[8px] shadow-sm border border-[var(--color-hairline-light)] p-6 shrink-0">
          <div className="mb-8">
            <label className="block text-body-strong mb-2 text-[var(--color-ink-deep)]">Độ khó AI</label>
            <select 
              value={difficulty} 
              onChange={(e) => setDifficulty(e.target.value as Difficulty)}
              disabled={isAiThinking || grid.some(r => r.some(c => c !== 0))}
              className="w-full p-3 rounded-[8px] border border-[var(--color-hairline-light)] bg-[var(--color-surface-card)] text-body-sm focus:outline-none focus:border-[var(--color-primary)] disabled:opacity-50 transition-colors"
            >
              <option value="easy">Dễ</option>
              <option value="medium">Trung bình</option>
              <option value="hard">Khó</option>
            </select>
            {grid.some(r => r.some(c => c !== 0)) && !winner && (
               <p className="text-[13px] text-[var(--color-ink)] opacity-60 mt-2">Chỉ có thể đổi độ khó khi bắt đầu ván mới.</p>
            )}
          </div>

          <div className="mb-8 p-5 rounded-[8px] bg-[var(--color-surface-card)] border border-[var(--color-hairline-light)]">
            <h3 className="text-body-strong mb-3 text-[var(--color-ink-deep)]">Trạng thái</h3>
            {winner !== null ? (
              <div className="flex items-center gap-2 text-[var(--color-primary)] font-medium">
                <Trophy size={20} />
                {winner === PLAYER_VAL ? 'Bạn đã thắng!' : winner === AI_VAL ? 'AI đã thắng!' : 'Hòa!'}
              </div>
            ) : (
              <div className="flex items-center gap-3">
                {turn === PLAYER_VAL ? (
                  <User size={20} className="text-[var(--color-primary)]" />
                ) : (
                  <Bot size={20} className="text-[var(--color-charcoal)] animate-pulse" />
                )}
                <span className="text-body-sm">
                  {turn === PLAYER_VAL ? 'Lượt của bạn (X)' : 'AI đang nghĩ... (O)'}
                </span>
              </div>
            )}
          </div>

          <button 
            onClick={handleRestart}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-full border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-[var(--color-on-primary)] transition-colors text-body-strong tracking-wide"
          >
            <RefreshCw size={18} />
            Chơi lại
          </button>
        </div>

        {/* Board - Modern Design */}
        <div className="bg-[var(--color-surface-card)] p-4 md:p-6 rounded-[8px] shadow-sm border border-[var(--color-hairline-light)]">
          <div 
            className="grid" 
            style={{ 
              gridTemplateColumns: `repeat(${GRID_SIZE}, minmax(24px, 40px))`,
              gap: '2px',
              backgroundColor: 'var(--color-hairline-light)',
              border: '2px solid var(--color-hairline-light)'
            }}
          >
            {grid.map((row, r) => 
              row.map((cell, c) => (
                <button
                  key={`${r}-${c}`}
                  onClick={() => handleCellClick(r, c)}
                  disabled={winner !== null || cell !== 0 || turn !== PLAYER_VAL || isAiThinking}
                  className="aspect-square bg-[var(--color-canvas-light)] flex items-center justify-center text-xl md:text-2xl font-bold transition-all duration-200 hover:bg-[var(--color-surface-soft)] disabled:hover:bg-[var(--color-canvas-light)]"
                >
                  {cell === PLAYER_VAL && <span className="text-[var(--color-primary)]">X</span>}
                  {cell === AI_VAL && <span className="text-[var(--color-ink)]">O</span>}
                </button>
              ))
            )}
          </div>
        </div>

      </main>
    </div>
  );
}
