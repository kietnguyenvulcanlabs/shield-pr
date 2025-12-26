"""
Sample React frontend code for testing Code Review Assistant.
"""

import React, { useState, useEffect } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

export function UserProfile({ userId }: { userId: number }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(data => {
        if (mounted) {
          setUser(data);
          setLoading(false);
        }
      })
      .catch(err => {
        if (mounted) {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      mounted = false;
    };
  }, [userId]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="profile">
      <h1>{user?.name}</h1>
      <p>{user?.email}</p>
      <button onClick={() => console.log('Edit clicked')}>
        Edit Profile
      </button>
    </div>
  );
}

export default UserProfile;
