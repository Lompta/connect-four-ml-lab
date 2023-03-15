import React, { useState, useCallback } from 'react';
import GamePiece from '../ConnectFourGamePiece';

const initialGameState = [
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0]
];

const ConnectFourGame = () => {
  const [gameState, setGameState] = useState(initialGameState);
  const [currentPlayer, setCurrentPlayer] = useState(1);
  const [winner, setWinner] = useState(0);

  const checkWin = useCallback((updatedGameState) => {
    // Horizontal check
    for (const row of updatedGameState) {
      for (let c = 0; c < 4; c++) {
        const horizontalSum = row.slice(c, c + 4).reduce((a, b) => a + b);
        if (Math.abs(horizontalSum) === 4) {
          return row[c];
        }
      }
    }

    // Vertical check
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 7; c++) {
        const verticalSum = updatedGameState[r][c] + updatedGameState[r + 1][c] + updatedGameState[r + 2][c] + updatedGameState[r + 3][c];
        if (Math.abs(verticalSum) === 4) {
          return updatedGameState[r][c];
        }
      }
    }

    // Diagonal check
    for (let r = 0; r < 3; r++) {
      for (let c = 0; c < 4; c++) {
        const diagonalSum1 = updatedGameState[r][c] + updatedGameState[r + 1][c + 1] + updatedGameState[r + 2][c + 2] + updatedGameState[r + 3][c + 3];
        const diagonalSum2 = updatedGameState[r][6 - c] + updatedGameState[r + 1][5 - c] + updatedGameState[r + 2][4 - c] + updatedGameState[r + 3][3 - c];
        if (Math.abs(diagonalSum1) === 4) {
          return updatedGameState[r][c];
        }
        if (Math.abs(diagonalSum2) === 4) {
          return updatedGameState[r][6 - c];
        }
      }
    }

    return 0;
  }, []);

  const handleColumnClick = useCallback((column) => {
    let reversedGameState = [...gameState].reverse();
    let moveMade = false;
    const updatedReversedGameState = reversedGameState.map((row) => {
      if (!moveMade && !row[column]) {
        const updatedRow = [...row];
        updatedRow[column] = currentPlayer;
        moveMade = true;
        return updatedRow;
      } else {
        return row;
      }
    });

    const updatedGameState = updatedReversedGameState.reverse();
    const detectedWinner = checkWin(updatedGameState);
    if (detectedWinner !== 0) {
      setWinner(detectedWinner);
    } else {
      if (currentPlayer === 1) {
        setCurrentPlayer(-1);
      } else {
        setCurrentPlayer(1);
      }
    }

    setGameState(updatedGameState);
  }, [currentPlayer, gameState, checkWin]);

  const handleApiMove = useCallback(async () => {
    const concatenatedGameState = gameState.reduce((acc, val) => acc.concat(val), []);
    const response = await fetch('http://localhost:5000/get_api_move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game: concatenatedGameState })
    });
    
    const responseJson = await response.json();
    handleColumnClick(responseJson["move"]);
  }, [gameState, handleColumnClick]);

  const resetGameState = useCallback(() => {
    setGameState([...initialGameState]);
    setCurrentPlayer(1);
    setWinner(0);
  }, []);

  return (
    <div>
      <ConnectFourBoard gameState={gameState} onColumnClick={handleColumnClick} />
      {winner !== 0 && <div>{winner === 1 ? "Yellow Wins" : "Red Wins"}</div>}
      <button onClick={handleApiMove} disabled={winner !== 0}>API Player's Turn</button>
      <button onClick={resetGameState}>Start Over</button>
    </div>
  );
};

const ConnectFourBoard = ({ gameState, onColumnClick }) => {
  return (
    <table>
      <tbody>
        {gameState.map((row, i) => (
          <tr key={i}>
            {row.map((cell, j) => (
              <td key={j} onClick={() => onColumnClick(j)}><GamePiece controllingPlayer={cell}/></td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ConnectFourGame;