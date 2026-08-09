import React from 'react';

interface AvatarProps {
  name?: string;
  avatarUrl?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const Avatar: React.FC<AvatarProps> = ({ 
  name = 'User', 
  avatarUrl, 
  size = 'md',
  className = ''
}) => {
  const sizes = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-12 h-12 text-lg',
    xl: 'w-32 h-32 text-4xl'
  };

  if (avatarUrl) {
    return (
      <img
        src={avatarUrl}
        alt={name}
        className={`rounded-full object-cover ${sizes[size]} ${className}`}
      />
    );
  }

  const initials = name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div
      className={`rounded-full bg-blue-600 text-white flex items-center justify-center font-semibold ${sizes[size]} ${className}`}
    >
      {initials || 'U'}
    </div>
  );
};

export default Avatar;