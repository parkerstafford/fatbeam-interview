'use client'

import React, { useState, useMemo } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, Target, Users } from 'lucide-react';

interface Opportunity {
  id: string;
  accountName: string;
  stage: string;
  product: string;
  amount: number;
  probability: number;
  region: string;
  owner: string;
  createdDate: string;
  closeDate: string;
  daysInStage: number;
}

interface Metrics {
  totalPipeline: number;
  weightedPipeline: number;
  winRate: number;
  totalRevenue: number;
  avgDealSize: number;
  totalOpps: number;
}

interface ChartData {
  stage?: string;
  name?: string;
  value: number;
  count?: number;
  pipeline?: number;
  closed?: number;
  [key: string]: string | number | undefined;
}

const generateSalesData = (): Opportunity[] => {
  const stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'];
  const products = ['Fiber Internet', 'Dark Fiber', 'Ethernet', 'Cloud Connect', 'Managed Services'];
  const regions = ['Northwest', 'Mountain West', 'Pacific', 'Southwest'];
  const reps = ['Sarah Johnson', 'Mike Chen', 'Emily Rodriguez', 'David Kim', 'Jessica Taylor'];
  
  const opportunities: Opportunity[] = [];
  const currentDate = new Date();
  
  for (let i = 0; i < 150; i++) {
    const createdDate = new Date(currentDate);
    createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 180));
    
    const closeDate = new Date(createdDate);
    closeDate.setDate(closeDate.getDate() + Math.floor(Math.random() * 90) + 30);
    
    const stage = stages[Math.floor(Math.random() * stages.length)];
    const probability = stage === 'Closed Won' ? 100 : 
                       stage === 'Closed Lost' ? 0 :
                       stage === 'Negotiation' ? 75 :
                       stage === 'Proposal' ? 50 :
                       stage === 'Qualification' ? 25 : 10;
    
    opportunities.push({
      id: `OPP-${1000 + i}`,
      accountName: `${['Acme Corp', 'TechStart Inc', 'Global Systems', 'Enterprise Co', 'Summit LLC', 'Valley Industries'][Math.floor(Math.random() * 6)]} ${i}`,
      stage,
      product: products[Math.floor(Math.random() * products.length)],
      amount: Math.floor(Math.random() * 150000) + 10000,
      probability,
      region: regions[Math.floor(Math.random() * regions.length)],
      owner: reps[Math.floor(Math.random() * reps.length)],
      createdDate: createdDate.toISOString().split('T')[0],
      closeDate: closeDate.toISOString().split('T')[0],
      daysInStage: Math.floor(Math.random() * 60) + 1
    });
  }
  
  return opportunities;
};

export default function Dashboard() {
  const [selectedRegion, setSelectedRegion] = useState<string>('All');
  const [selectedRep, setSelectedRep] = useState<string>('All');
  const [dateRange, setDateRange] = useState<string>('90');
  
  const allData = useMemo(() => generateSalesData(), []);
  
  const filteredData = useMemo(() => {
    return allData.filter(opp => {
      const regionMatch = selectedRegion === 'All' || opp.region === selectedRegion;
      const repMatch = selectedRep === 'All' || opp.owner === selectedRep;
      
      const daysAgo = new Date();
      daysAgo.setDate(daysAgo.getDate() - parseInt(dateRange));
      const oppDate = new Date(opp.createdDate);
      const dateMatch = oppDate >= daysAgo;
      
      return regionMatch && repMatch && dateMatch;
    });
  }, [allData, selectedRegion, selectedRep, dateRange]);
  
  const metrics = useMemo((): Metrics => {
    const totalPipeline = filteredData
      .filter(o => !o.stage.includes('Closed'))
      .reduce((sum, o) => sum + o.amount, 0);
    
    const weightedPipeline = filteredData
      .filter(o => !o.stage.includes('Closed'))
      .reduce((sum, o) => sum + (o.amount * o.probability / 100), 0);
    
    const closedWon = filteredData.filter(o => o.stage === 'Closed Won');
    const closedLost = filteredData.filter(o => o.stage === 'Closed Lost');
    const totalClosed = closedWon.length + closedLost.length;
    const winRate = totalClosed > 0 ? (closedWon.length / totalClosed * 100) : 0;
    
    const totalRevenue = closedWon.reduce((sum, o) => sum + o.amount, 0);
    
    const avgDealSize = filteredData.length > 0 ? 
      filteredData.reduce((sum, o) => sum + o.amount, 0) / filteredData.length : 0;
    
    return {
      totalPipeline,
      weightedPipeline,
      winRate,
      totalRevenue,
      avgDealSize,
      totalOpps: filteredData.length
    };
  }, [filteredData]);
  
  const pipelineByStage = useMemo((): ChartData[] => {
    const stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'];
    return stages.map(stage => ({
      stage,
      value: filteredData.filter(o => o.stage === stage).reduce((sum, o) => sum + o.amount, 0),
      count: filteredData.filter(o => o.stage === stage).length
    }));
  }, [filteredData]);
  
  const revenueByProduct = useMemo((): ChartData[] => {
    const products: { [key: string]: number } = {};
    filteredData.forEach(opp => {
      if (!products[opp.product]) products[opp.product] = 0;
      products[opp.product] += opp.amount;
    });
    return Object.entries(products).map(([name, value]) => ({ name, value }));
  }, [filteredData]);

  const salesByRep = useMemo((): ChartData[] => {
    const reps: { [key: string]: ChartData } = {};
    filteredData.forEach(opp => {
      if (!reps[opp.owner]) {
        reps[opp.owner] = { name: opp.owner, pipeline: 0, closed: 0, count: 0, value: 0 };
      }
      reps[opp.owner].count! += 1;
      if (opp.stage === 'Closed Won') {
        reps[opp.owner].closed! += opp.amount;
      } else if (!opp.stage.includes('Closed')) {
        reps[opp.owner].pipeline! += opp.amount;
      }
    });
    return Object.values(reps);
  }, [filteredData]);
  
  const pipelineByRegion = useMemo((): ChartData[] => {
    const regions: { [key: string]: number } = {};
    filteredData.forEach(opp => {
      if (!regions[opp.region]) regions[opp.region] = 0;
      if (!opp.stage.includes('Closed')) {
        regions[opp.region] += opp.amount;
      }
    });
    return Object.entries(regions).map(([name, value]) => ({ name, value }));
  }, [filteredData]);
  
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
  
  const regions = ['All', 'Northwest', 'Mountain West', 'Pacific', 'Southwest'];
  const reps = ['All', ...Array.from(new Set(allData.map(o => o.owner)))];
  
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Sales Pipeline Analytics</h1>
          <p className="text-blue-200">Real-time sales performance tracking and forecasting</p>
        </div>
        
        <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 mb-6 border border-white/20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-blue-200 mb-2">Region</label>
              <select 
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                {regions.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-blue-200 mb-2">Sales Rep</label>
              <select 
                value={selectedRep}
                onChange={(e) => setSelectedRep(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                {reps.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-blue-200 mb-2">Date Range</label>
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="w-full px-4 py-2 rounded-lg bg-white/20 text-white border border-white/30 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="30">Last 30 Days</option>
                <option value="60">Last 60 Days</option>
                <option value="90">Last 90 Days</option>
                <option value="180">Last 180 Days</option>
              </select>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-8 h-8 opacity-80" />
              <span className="text-sm font-medium">Total Pipeline</span>
            </div>
            <div className="text-3xl font-bold">{formatCurrency(metrics.totalPipeline)}</div>
            <div className="text-sm opacity-80 mt-1">Weighted: {formatCurrency(metrics.weightedPipeline)}</div>
          </div>
          
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="w-8 h-8 opacity-80" />
              <span className="text-sm font-medium">Total Revenue</span>
            </div>
            <div className="text-3xl font-bold">{formatCurrency(metrics.totalRevenue)}</div>
            <div className="text-sm opacity-80 mt-1">Closed Won</div>
          </div>
          
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <Target className="w-8 h-8 opacity-80" />
              <span className="text-sm font-medium">Win Rate</span>
            </div>
            <div className="text-3xl font-bold">{metrics.winRate.toFixed(1)}%</div>
            <div className="text-sm opacity-80 mt-1">Close Rate</div>
          </div>
          
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white shadow-xl">
            <div className="flex items-center justify-between mb-2">
              <Users className="w-8 h-8 opacity-80" />
              <span className="text-sm font-medium">Avg Deal Size</span>
            </div>
            <div className="text-3xl font-bold">{formatCurrency(metrics.avgDealSize)}</div>
            <div className="text-sm opacity-80 mt-1">{metrics.totalOpps} Opportunities</div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Pipeline by Stage</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pipelineByStage}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="stage" tick={{ fill: '#fff', fontSize: 12 }} angle={-45} textAnchor="end" height={100} />
                <YAxis tick={{ fill: '#fff' }} tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                  formatter={(value: number) => formatCurrency(value)}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Revenue by Product</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={revenueByProduct}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {revenueByProduct.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Sales Performance by Rep</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={salesByRep}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" tick={{ fill: '#fff', fontSize: 11 }} angle={-45} textAnchor="end" height={100} />
                <YAxis tick={{ fill: '#fff' }} tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                  formatter={(value: number) => formatCurrency(value)}
                />
                <Legend />
                <Bar dataKey="pipeline" fill="#3b82f6" name="Pipeline" radius={[8, 8, 0, 0]} />
                <Bar dataKey="closed" fill="#10b981" name="Closed Won" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-white/10 backdrop-blur-md rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Pipeline by Region</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pipelineByRegion} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis type="number" tick={{ fill: '#fff' }} tickFormatter={(val) => `$${(val/1000).toFixed(0)}K`} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#fff' }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: 'none', borderRadius: '8px' }}
                  formatter={(value: number) => formatCurrency(value)}
                />
                <Bar dataKey="value" fill="#f59e0b" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="mt-8 text-center text-blue-200 text-sm">
          <p>Sales Analytics Dashboard | Built with Next.js + TypeScript</p>
        </div>
      </div>
    </div>
  );
}