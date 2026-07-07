import React from 'react';

interface Props {
  platform: 'kalshi' | 'polymarket' | string;
}

const PlatformBadge: React.FC<Props> = ({ platform }) => {
  const isKalshi = platform.toLowerCase() === 'kalshi';
  const className = `badge ${isKalshi ? 'badge-kalshi' : 'badge-polymarket'}`;
  
  return (
    <span className={className}>
      {platform}
    </span>
  );
};

export default PlatformBadge;
