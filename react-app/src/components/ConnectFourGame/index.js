import React, { useState, useCallback } from 'react';
import GamePiece from '../ConnectFourGamePiece';

const ConnectFourGame = () => {
  const [gameState, setGameState] = useState([
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0]
  ]);
  const [currentPlayer, setCurrentPlayer] = useState(1);

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

    if(currentPlayer === 1) {
      setCurrentPlayer(-1);
    } else {
      setCurrentPlayer(1);
    }

    setGameState(updatedReversedGameState.reverse());
  }, [currentPlayer, gameState]);

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

  return (
    <div>
      <ConnectFourBoard gameState={gameState} onColumnClick={handleColumnClick} />
      <button onClick={handleApiMove}>API Player's Turn</button>
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