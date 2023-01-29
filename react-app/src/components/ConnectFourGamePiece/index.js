import React, { useMemo } from 'react';
import './styles.css';

const GamePiece = ({ onClick, controllingPlayer }) => {
  const color = useMemo(() => {
    if (controllingPlayer === 1) {
        return 'yellow';
    } else if (controllingPlayer === -1) {
        return 'red';
    }
  }, [controllingPlayer]);

  return (
    <div onClick={onClick} className={`game-piece ${color}`} />
  );
}

export default GamePiece;