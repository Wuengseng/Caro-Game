export type Difficulty = 'easy' | 'medium' | 'hard';

export const getAIMove = async (
  grid: number[][],
  difficulty: Difficulty,
  ai_player: number,
  player: number
) => {
  const response = await fetch('http://127.0.0.1:8000/move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ grid, difficulty, ai_player, player })
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch AI move');
  }
  
  return response.json();
};
