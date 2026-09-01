import React from 'react';
import { Severity, Category } from '../types';
import { 
  AlertOctagon, 
  AlertTriangle, 
  Info, 
  CheckCircle2, 
  Smartphone, 
  Layout, 
  FileText, 
  Eye, 
  Gauge, 
  Terminal, 
  Wifi, 
  Split 
} from 'lucide-react';

interface SeverityBadgeProps {
  severity: Severity;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const styles: Record<Severity, { bg: string; text: string; border: string; icon: React.FC<{ className?: string }> }> = {
    critical: {
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      icon: AlertOctagon
    },
    high: {
      bg: 'bg-orange-500/10',
      text: 'text-orange-400',
      border: 'border-orange-500/30',
      icon: AlertTriangle
    },
    medium: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      icon: AlertTriangle
    },
    low: {
      bg: 'bg-blue-500/10',
      text: 'text-blue-400',
      border: 'border-blue-500/30',
      icon: Info
    },
    info: {
      bg: 'bg-slate-500/10',
      text: 'text-slate-400',
      border: 'border-slate-500/30',
      icon: Info
    }
  };

  const current = styles[severity] || styles.info;
  const Icon = current.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border uppercase tracking-wider ${current.bg} ${current.text} ${current.border}`}>
      <Icon className="h-3 w-3" />
      {severity}
    </span>
  );
};

interface CategoryBadgeProps {
  category: Category;
}

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category }) => {
  const catIcons: Record<string, React.FC<{ className?: string }>> = {
    ui: Layout,
    responsive: Smartphone,
    functional: CheckCircle2,
    forms: FileText,
    accessibility: Eye,
    performance: Gauge,
    javascript: Terminal,
    network: Wifi,
    visual_regression: Split
  };

  const Icon = catIcons[category.toLowerCase()] || Layout;

  return (
    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-800 text-slate-300 border border-slate-700">
      <Icon className="h-3 w-3 text-slate-400" />
      {category.replace('_', ' ').toUpperCase()}
    </span>
  );
};
