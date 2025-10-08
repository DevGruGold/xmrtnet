import React, { useState, useEffect } from 'react';
import config from '../config';

const ElizaActivity = () => {
  const [activities, setActivities] = useState([]);
  const [state, setState] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Fetch Eliza activity from API
  const fetchActivity = async () => {
    try {
      const response = await fetch(`${config.API_URL}${config.endpoints.elizaActivity}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setActivities(data.activities || []);
        setState(data.state);
        setError(null);
        setLastUpdate(new Date());
      } else {
        setError(data.error || 'Failed to fetch activity');
      }
    } catch (err) {
      console.error('Error fetching activity:', err);
      setError('Unable to connect to Eliza API');
    } finally {
      setLoading(false);
    }
  };

  // Fetch Eliza stats
  const fetchStats = async () => {
    try {
      const response = await fetch(`${config.API_URL}${config.endpoints.elizaStats}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchActivity();
    fetchStats();
  }, []);

  // Set up polling for realtime updates
  useEffect(() => {
    if (!config.features.realtimeActivity) return;

    const interval = setInterval(() => {
      fetchActivity();
      fetchStats();
    }, config.ACTIVITY_POLL_INTERVAL);

    return () => clearInterval(interval);
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      self_improvement: '#8b5cf6',
      tool_discovery: '#3b82f6',
      utility_creation: '#10b981',
      cycle_completion: '#f59e0b',
      general: '#6b7280'
    };
    return colors[category] || colors.general;
  };

  if (loading) {
    return (
      <div className="eliza-activity-page fade-in">
        <h1 className="page-title">Eliza Activity</h1>
        <div style={{
          textAlign: 'center',
          padding: '3rem 1rem',
          color: 'rgba(255, 255, 255, 0.6)'
        }}>
          <div className="loading-spinner" style={{
            width: '40px',
            height: '40px',
            border: '4px solid rgba(255, 255, 255, 0.1)',
            borderTop: '4px solid #8b5cf6',
            borderRadius: '50%',
            margin: '0 auto 1rem',
            animation: 'spin 1s linear infinite'
          }}></div>
          <p>Loading Eliza activity...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="eliza-activity-page fade-in">
      <h1 className="page-title">Eliza Activity</h1>
      
      {/* Stats Overview */}
      {stats && (
        <div className="stats-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          <div className="stat-card" style={{
            background: 'rgba(139, 92, 246, 0.1)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '12px',
            padding: '1rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔄</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#8b5cf6' }}>
              {stats.cycle_count}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
              Cycles
            </div>
          </div>

          <div className="stat-card" style={{
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '12px',
            padding: '1rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3b82f6' }}>
              {stats.total_tools_discovered || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
              Tools Found
            </div>
          </div>

          <div className="stat-card" style={{
            background: 'rgba(16, 185, 129, 0.1)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '12px',
            padding: '1rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🛠️</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981' }}>
              {stats.total_utilities || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
              Utilities
            </div>
          </div>

          <div className="stat-card" style={{
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '12px',
            padding: '1rem',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#f59e0b' }}>
              {stats.total_commits || 0}
            </div>
            <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
              Commits
            </div>
          </div>
        </div>
      )}

      {/* Current State */}
      {state && (
        <div style={{
          background: 'rgba(139, 92, 246, 0.1)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '2rem'
        }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', color: '#8b5cf6' }}>
            🧠 Current State
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div>
              <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>Cycle Count</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{state.cycle_count}</div>
            </div>
            <div>
              <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>Improvements</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{state.total_improvements || 0}</div>
            </div>
            <div>
              <div style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>Last Run</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
                {state.last_run ? formatDate(state.last_run) : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          padding: '1rem',
          marginBottom: '2rem',
          color: '#ef4444'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Activity List */}
      <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.25rem', color: '#ffffff' }}>Recent Activity</h2>
        {lastUpdate && (
          <div style={{ fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.5)' }}>
            Updated {formatDate(lastUpdate)}
          </div>
        )}
      </div>

      <div className="activity-list">
        {activities.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem 1rem',
            color: 'rgba(255, 255, 255, 0.6)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</div>
            <h3 style={{ marginBottom: '0.5rem', color: '#ffffff' }}>No activity yet</h3>
            <p>Eliza's self-improvement activities will appear here</p>
          </div>
        ) : (
          activities.map((activity, index) => (
            <div key={`${activity.sha}-${index}`} className="activity-item" style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              padding: '1.5rem',
              marginBottom: '1rem',
              transition: 'all 0.3s ease',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
              e.currentTarget.style.borderColor = getCategoryColor(activity.category);
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{
                  fontSize: '2rem',
                  minWidth: '40px',
                  textAlign: 'center'
                }}>
                  {activity.icon}
                </div>
                
                <div style={{ flex: 1 }}>
                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    marginBottom: '0.5rem'
                  }}>
                    <div>
                      <div style={{
                        fontSize: '1rem',
                        fontWeight: '600',
                        color: '#ffffff',
                        marginBottom: '0.25rem'
                      }}>
                        {activity.message}
                      </div>
                      <div style={{
                        display: 'inline-block',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        background: `${getCategoryColor(activity.category)}20`,
                        color: getCategoryColor(activity.category),
                        textTransform: 'capitalize'
                      }}>
                        {activity.category.replace('_', ' ')}
                      </div>
                    </div>
                    
                    <div style={{ textAlign: 'right' }}>
                      <div style={{
                        fontSize: '0.875rem',
                        color: 'rgba(255, 255, 255, 0.6)',
                        marginBottom: '0.25rem'
                      }}>
                        {formatDate(activity.timestamp)}
                      </div>
                      <div style={{
                        fontSize: '0.75rem',
                        color: 'rgba(255, 255, 255, 0.4)',
                        fontFamily: 'monospace'
                      }}>
                        {activity.sha}
                      </div>
                    </div>
                  </div>
                  
                  {activity.files_changed > 0 && (
                    <div style={{
                      fontSize: '0.875rem',
                      color: 'rgba(255, 255, 255, 0.5)',
                      marginTop: '0.5rem'
                    }}>
                      📄 {activity.files_changed} file{activity.files_changed !== 1 ? 's' : ''} changed
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {activities.length > 0 && (
        <div style={{
          textAlign: 'center',
          padding: '2rem 1rem',
          color: 'rgba(255, 255, 255, 0.6)'
        }}>
          <p>Showing {activities.length} recent activit{activities.length !== 1 ? 'ies' : 'y'}</p>
          <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Updates every {config.ACTIVITY_POLL_INTERVAL / 1000} seconds
          </p>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .fade-in {
          animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default ElizaActivity;
