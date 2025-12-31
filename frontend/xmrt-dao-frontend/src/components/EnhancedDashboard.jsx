import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Shield, 
  Cpu,
  Bell,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const EnhancedDashboard = () => {
  const [metrics, setMetrics] = useState({
    activeMiners: 1247,
    proposals: 15,
    treasuryValue: 2600000,
    uptime: 99.9,
    cycleNumber: 750
  });

  const [agents, setAgents] = useState([
    { name: 'Eliza Core', status: 'online', icon: '🧠', responseTime: '145ms' },
    { name: 'DAO Agent', status: 'online', icon: '🏛️', responseTime: '162ms' },
    { name: 'Mining Agent', status: 'online', icon: '⛏️', responseTime: '128ms' },
    { name: 'Treasury Agent', status: 'online', icon: '💰', responseTime: '134ms' },
    { name: 'Governance Agent', status: 'online', icon: '🗳️', responseTime: '157ms' }
  ]);

  const [notifications] = useState([
    { id: 1, type: 'success', message: 'Analytics cycle #750 completed successfully', time: '2 min ago' },
    { id: 2, type: 'info', message: 'New proposal submitted for voting', time: '1 hour ago' },
    { id: 3, type: 'success', message: '1,200+ active miners milestone achieved', time: '3 hours ago' },
    { id: 4, type: 'info', message: 'Treasury health report available', time: '5 hours ago' }
  ]);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        activeMiners: prev.activeMiners + Math.floor(Math.random() * 5),
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value);
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-4 md:p-6">
      {/* Enhanced Header */}
      <div className="mb-6 md:mb-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 md:p-8 text-white shadow-2xl animate-gradient">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="text-center md:text-left">
            <h1 className="text-3xl md:text-4xl font-bold mb-2 flex items-center justify-center md:justify-start gap-2">
              <span className="animate-pulse">🌐</span>
              XMRT DAO Dashboard
            </h1>
            <p className="text-purple-100 text-base md:text-lg">
              Enhanced Autonomous System • Real-Time Analytics • AI-Powered
            </p>
          </div>
          <button 
            className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-xl transition-all flex items-center gap-2 hover:scale-105"
            onClick={handleRefresh}
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6 md:mb-8">
        <MetricCard
          title="Active Miners"
          value={metrics.activeMiners.toLocaleString()}
          icon={<Activity className="w-6 h-6" />}
          trend="+89"
          color="purple"
        />
        <MetricCard
          title="DAO Proposals"
          value={metrics.proposals}
          icon={<Users className="w-6 h-6" />}
          trend="+3"
          color="blue"
        />
        <MetricCard
          title="Treasury Value"
          value={formatCurrency(metrics.treasuryValue)}
          icon={<DollarSign className="w-6 h-6" />}
          trend="+$200K"
          color="green"
        />
        <MetricCard
          title="Network Uptime"
          value={`${metrics.uptime}%`}
          icon={<Shield className="w-6 h-6" />}
          trend="+0.1%"
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
        {/* Agent Status */}
        <Card className="lg:col-span-2 shadow-lg hover:shadow-xl transition-all">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="w-5 h-5" />
              Agent Status
              <Badge className="ml-auto bg-green-500 hover:bg-green-600">
                {agents.filter(a => a.status === 'online').length}/{agents.length} Online
              </Badge>
            </CardTitle>
            <CardDescription>Real-time agent monitoring & performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {agents.map((agent, idx) => (
                <div 
                  key={idx}
                  className="flex items-center justify-between p-3 md:p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all hover:scale-[1.02]"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{agent.icon}</span>
                    <div>
                      <p className="font-semibold text-sm md:text-base">{agent.name}</p>
                      <p className="text-xs md:text-sm text-gray-500">Response: {agent.responseTime}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {agent.status === 'online' ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    )}
                    <Badge 
                      className={agent.status === 'online' 
                        ? 'bg-green-500 hover:bg-green-600' 
                        : 'bg-red-500 hover:bg-red-600'
                      }
                    >
                      {agent.status === 'online' ? 'Online' : 'Offline'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Notifications */}
        <Card className="shadow-lg hover:shadow-xl transition-all">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              Notifications
              <Badge className="ml-auto bg-purple-500 hover:bg-purple-600">
                {notifications.length}
              </Badge>
            </CardTitle>
            <CardDescription>Recent system events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {notifications.map((notif) => (
                <div 
                  key={notif.id}
                  className={`p-3 rounded-lg border-l-4 transition-all hover:scale-[1.02] ${
                    notif.type === 'success' 
                      ? 'bg-green-50 border-green-500 hover:bg-green-100' 
                      : 'bg-blue-50 border-blue-500 hover:bg-blue-100'
                  }`}
                >
                  <p className="text-sm font-medium">{notif.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Cycle */}
      <Card className="shadow-lg hover:shadow-xl transition-all mb-6 md:mb-8">
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <CardTitle className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5" />
                Latest Analytics Cycle
              </CardTitle>
              <CardDescription>Cycle #{metrics.cycleNumber} - Automated Analysis</CardDescription>
            </div>
            <Badge className="bg-green-500 hover:bg-green-600 w-fit">
              <span className="inline-block w-2 h-2 bg-white rounded-full animate-pulse mr-2"></span>
              Active
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2 text-sm md:text-base">
                💡 Key Insights
              </h4>
              <div className="space-y-2">
                <InsightBadge text="Mining network growth accelerating" />
                <InsightBadge text="Strong governance participation" />
                <InsightBadge text="Treasury health excellent" />
                <InsightBadge text="Security measures optimal" />
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2 text-sm md:text-base">
                🎯 Recommendations
              </h4>
              <div className="space-y-2">
                <RecommendationBadge text="Continue automated optimization" />
                <RecommendationBadge text="Expand metrics collection" />
                <RecommendationBadge text="Strengthen cross-chain integration" />
              </div>
            </div>
          </div>
          <div className="mt-6">
            <div className="flex justify-between mb-2 text-sm">
              <span className="font-medium">Next Cycle Progress</span>
              <span className="text-gray-500">4h 23m remaining</span>
            </div>
            <Progress value={68} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center text-gray-600 text-sm bg-white/70 backdrop-blur-sm rounded-xl p-4 md:p-6 shadow-lg">
        <p className="font-semibold mb-1">🌐 XMRT DAO - Enhanced Dashboard v3.1.0</p>
        <p className="text-xs md:text-sm">Powered by ElizaOS • Real-time Monitoring • AI-Driven Analytics</p>
        <p className="mt-2 text-xs">
          <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></span>
          <span className="text-green-600 font-semibold">All Systems Operational</span>
          <span className="mx-2">•</span>
          Uptime: {metrics.uptime}%
          <span className="mx-2">•</span>
          {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, trend, color }) => {
  const colorClasses = {
    purple: 'from-purple-500 to-purple-600',
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    emerald: 'from-emerald-500 to-emerald-600'
  };

  return (
    <Card className="shadow-lg hover:shadow-xl transition-all hover:-translate-y-1">
      <CardContent className="p-4 md:p-6">
        <div className="flex justify-between items-start mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]} text-white shadow-md`}>
            {icon}
          </div>
          <Badge className="bg-green-100 text-green-700 hover:bg-green-200 border-green-300">
            {trend}
          </Badge>
        </div>
        <p className="text-gray-600 text-sm font-medium mb-1">{title}</p>
        <p className="text-2xl md:text-3xl font-bold">{value}</p>
      </CardContent>
    </Card>
  );
};

const InsightBadge = ({ text }) => (
  <div className="flex items-start gap-2 p-2 md:p-3 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors">
    <span className="text-sm md:text-base">✨</span>
    <span className="text-xs md:text-sm flex-1">{text}</span>
  </div>
);

const RecommendationBadge = ({ text }) => (
  <div className="flex items-start gap-2 p-2 md:p-3 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
    <span className="text-sm md:text-base">🎯</span>
    <span className="text-xs md:text-sm flex-1">{text}</span>
  </div>
);

export default EnhancedDashboard;
