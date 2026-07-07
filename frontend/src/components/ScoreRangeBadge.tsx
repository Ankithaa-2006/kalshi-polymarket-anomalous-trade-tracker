import React from 'react';

interface Props {
  score: number;
}

const ScoreRangeBadge: React.FC<Props> = ({ score }) => {
  let className = 'badge ';
  let text = '';

  if (score >= 5) {
    className += 'badge-score-high';
    text = '5+';
  } else if (score >= 4) {
    className += 'badge-score-medium';
    text = '4-5';
  } else if (score >= 3) {
    className += 'badge-score-low';
    text = '3-4';
  } else {
    className += 'badge-sentiment-neutral';
    text = '<3';
  }

  return (
    <span className={className}>
      {score.toFixed(1)} ({text})
    </span>
  );
};

export default ScoreRangeBadge;
