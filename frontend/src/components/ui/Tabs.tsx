'use client';

import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

export interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
  progress?: {
    total: number;
    answered: number; // Changed from 'completed' to match existing getProgress function
    percent: number;
  };
  disabled?: boolean;
}

export interface NestedTabItem extends TabItem {
  subTabs?: TabItem[];
}

export interface TabsProps {
  tabs: NestedTabItem[];
  defaultTab?: string;
  defaultSubTab?: string;
  className?: string;
  variant?: 'default' | 'agricultural';
  sticky?: boolean;
  onTabChange?: (tabId: string, subTabId?: string) => void;
}

export function Tabs({
  tabs,
  defaultTab,
  defaultSubTab,
  className,
  variant = 'agricultural',
  sticky = false,
  onTabChange
}: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id);
  const [activeSubTab, setActiveSubTab] = useState<string | null>(null);

  // Update active sub-tab when main tab changes
  useEffect(() => {
    const currentTab = tabs.find(tab => tab.id === activeTab);
    if (currentTab?.subTabs && currentTab.subTabs.length > 0) {
      const newSubTab = defaultSubTab || currentTab.subTabs[0].id;
      setActiveSubTab(newSubTab);
    } else {
      setActiveSubTab(null);
    }
  }, [activeTab, defaultSubTab]);

  const handleTabClick = (tabId: string) => {
    setActiveTab(tabId);
    const tab = tabs.find(t => t.id === tabId);
    const subTabId = tab?.subTabs?.[0]?.id || null;
    setActiveSubTab(subTabId);
    onTabChange?.(tabId, subTabId || undefined);
  };

  const handleSubTabClick = (subTabId: string) => {
    setActiveSubTab(subTabId);
    onTabChange?.(activeTab, subTabId);
  };

  const currentTab = tabs.find(tab => tab.id === activeTab);
  const currentSubTab = currentTab?.subTabs?.find(subTab => subTab.id === activeSubTab);

  const getProgressBarColor = (percent: number, isActive: boolean) => {
    if (!isActive) return 'bg-muted';
    return percent === 100 ? 'bg-success' : 'bg-primary';
  };

  const getTabStyles = (isActive: boolean, level: 'main' | 'sub' = 'main') => {
    const baseStyles = "relative font-bold border border-b-0 border-border whitespace-nowrap transition-all duration-200";
    
    if (variant === 'agricultural') {
      if (level === 'main') {
        return cn(baseStyles, 
          "px-4 py-2 text-base min-w-[120px]",
          isActive
            ? "bg-card text-primary shadow-md z-20 border-t-2 border-x-2 border-b-0 border-primary rounded-t-2xl -mb-[2px]"
            : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground z-10 border-t border-x border-b-0 border-border rounded-t-2xl mb-0"
        );
      } else {
        return cn(baseStyles,
          "px-3 py-1.5 font-semibold text-sm min-w-[100px]",
          isActive
            ? "bg-card text-success shadow z-20 border-t-2 border-x-2 border-b-0 border-success rounded-t-xl -mb-[2px]"
            : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground z-10 border-t border-x border-b-0 border-border rounded-t-xl mb-0"
        );
      }
    }
    
    // Default variant
    return cn(baseStyles,
      "px-4 py-2 rounded-t-lg",
      isActive
        ? "bg-white text-blue-600 border-blue-500"
        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
    );
  };

  return (
    <div className={cn('w-full', className)}>
      {/* Main Tabs */}
      <div className={cn(
        'mb-2 flex flex-wrap gap-1 border-b-2 border-border bg-card',
        sticky && 'sticky top-0 z-20'
      )}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <div key={tab.id} className="flex flex-col items-center min-w-0">
              <button
                className={getTabStyles(isActive, 'main')}
                style={{ marginBottom: isActive ? '-2px' : '0' }}
                onClick={() => !tab.disabled && handleTabClick(tab.id)}
                disabled={tab.disabled}
                title={tab.label}
              >
                <span className="block">{tab.label}</span>
              </button>
              
              {/* Progress Bar for Main Tab */}
              {tab.progress && (
                <div className="w-full h-2 mt-2 bg-muted rounded-full overflow-hidden min-w-[60px]">
                  <div
                    className={cn(
                      "h-2 rounded-full transition-all duration-300",
                      getProgressBarColor(tab.progress.percent, isActive)
                    )}
                    style={{ width: `${tab.progress.percent}%` }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Sub Tabs */}
      {currentTab?.subTabs && currentTab.subTabs.length > 0 && (
        <div className={cn(
          'mb-4 overflow-x-auto border-b-2 border-border bg-card',
          sticky && 'sticky top-[56px] z-10'
        )}>
          <div className="flex gap-1">
            {currentTab.subTabs.map((subTab) => {
              const isActive = activeSubTab === subTab.id;
              return (
                <div key={subTab.id} className="flex flex-col items-center min-w-0">
                  <button
                    className={getTabStyles(isActive, 'sub')}
                    style={{ marginBottom: isActive ? '-2px' : '0' }}
                    onClick={() => !subTab.disabled && handleSubTabClick(subTab.id)}
                    disabled={subTab.disabled}
                    title={subTab.label}
                  >
                    <span className="block">{subTab.label}</span>
                  </button>
                  
                  {/* Progress Bar for Sub Tab */}
                  {subTab.progress && (
                    <div className="w-full h-1.5 mt-1 bg-muted rounded-full overflow-hidden min-w-[50px]">
                      <div
                        className={cn(
                          "h-1.5 rounded-full transition-all duration-300",
                          getProgressBarColor(subTab.progress.percent, isActive)
                        )}
                        style={{ width: `${subTab.progress.percent}%` }}
                      />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab Content */}
      <div className="mt-4">
        {currentSubTab ? currentSubTab.content : currentTab?.content}
      </div>
    </div>
  );
}

// Utility component for simple single-level tabs
export interface SimpleTabsProps {
  tabs: TabItem[];
  defaultTab?: string;
  className?: string;
  variant?: 'default' | 'agricultural';
  onTabChange?: (tabId: string) => void;
}

export function SimpleTabs({ tabs, ...props }: SimpleTabsProps) {
  const nestedTabs: NestedTabItem[] = tabs.map(tab => ({
    ...tab,
    subTabs: undefined
  }));

  return (
    <Tabs 
      {...props} 
      tabs={nestedTabs} 
      onTabChange={(tabId) => props.onTabChange?.(tabId)}
    />
  );
}