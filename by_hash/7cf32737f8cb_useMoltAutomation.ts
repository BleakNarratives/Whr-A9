'use client';

import { useEffect, useCallback, useState, useRef } from 'react';
import { useMolt } from './useMolt';
import { useSentinel } from './useSentinel';

interface SecurityAlertEvent extends CustomEvent {
  detail: {
    event: string;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    timestamp: string;
  };
}

/**
 * useMoltAutomation - Autonomous trigger system for Molt recursive improvement.
 * Listens for system activity and security events to trigger improvements "within reason".
 */
export const useMoltAutomation = () => {
  const { triggerMolt, level, isImproving } = useMolt();
  const { logSecurityEvent, rotateDecoys, checkBlacklist, triggerBlacklist } = useSentinel();
  const [cyclesRun, setCyclesRun] = useState(0);
  const [isLockdown, setIsLockdown] = useState(false);
  const [isBlacklisted, setIsBlacklisted] = useState(false); // FIX: was called but never declared
  const lockdownTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const MAX_AUTONOMOUS_CYCLES = 5;

  // FIX 1: cleanup timer on unmount to prevent memory leak / state update on dead component
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const checkLockdown = () => {
      const stored = localStorage.getItem('sentinel_lockdown');
      if (stored) {
        const lockdownExpiry = parseInt(stored, 10);
        if (Date.now() < lockdownExpiry) {
          setIsLockdown(true);
          const remaining = lockdownExpiry - Date.now();
          lockdownTimerRef.current = setTimeout(() => setIsLockdown(false), remaining);
        } else {
          localStorage.removeItem('sentinel_lockdown');
          setIsLockdown(false);
        }
      }
    };

    checkLockdown();

    return () => {
      if (lockdownTimerRef.current) clearTimeout(lockdownTimerRef.current);
    };
  }, []);

  const triggerLockdown = useCallback(() => {
    const expiry = Date.now() + (5 * 60 * 1000);
    localStorage.setItem('sentinel_lockdown', expiry.toString());
    setIsLockdown(true);
    logSecurityEvent('SYSTEM LOCKDOWN INITIATED: 5-minute cooldown active.', 'CRITICAL');
    if (lockdownTimerRef.current) clearTimeout(lockdownTimerRef.current);
    lockdownTimerRef.current = setTimeout(() => setIsLockdown(false), 5 * 60 * 1000);
  }, [logSecurityEvent]);

  const attemptAutonomousImprovement = useCallback(async (reason: string) => {
    if (cyclesRun >= MAX_AUTONOMOUS_CYCLES) {
      console.log(`[🤖 MOLT] Maximum autonomous cycles (${MAX_AUTONOMOUS_CYCLES}) reached. Awaiting manual override.`);
      return;
    }
    if (isImproving) return;
    console.log(`[🤖 MOLT] Autonomous trigger activated: ${reason}`);
    logSecurityEvent(`Autonomous Molt cycle ${cyclesRun + 1} triggered: ${reason}`, 'MEDIUM');
    setCyclesRun(prev => prev + 1);
    await triggerMolt();
  }, [triggerMolt, isImproving, logSecurityEvent, cyclesRun]);

  useEffect(() => {
    const handleSecurityAlert = (e: Event) => {
      const securityEvent = e as SecurityAlertEvent;
      const { severity, event } = securityEvent.detail;

      if (severity === 'HIGH' || severity === 'CRITICAL') {
        // FIX 2: safe JSON.parse — corrupted storage won't crash the security handler
        const alerts = (() => {
          try {
            const data = JSON.parse(localStorage.getItem('sentinel_alert_history') || '[]');
            return Array.isArray(data) ? data : [];
          } catch { return []; }
        })();

        const now = Date.now();
        const recentAlerts = [...alerts.filter((a: number) => now - a < 300000), now];
        localStorage.setItem('sentinel_alert_history', JSON.stringify(recentAlerts));

        if (recentAlerts.length >= 3 && !isLockdown) {
          triggerLockdown();
        }

        attemptAutonomousImprovement(`Security hardening required: ${event}`);
      }
    };

    const handleShadowRecorded = (e: Event) => {
      const customEvent = e as CustomEvent;
      const count = customEvent.detail?.count || 0;
      if (count >= 5) {
        attemptAutonomousImprovement(`Shadow Sequence detected (${count} logs). Initiating autonomous reconstruction.`);
      }
    };

    const handleDecoyBreach = () => {
      rotateDecoys();
      const key = 'sentinel_decoy_breaches';
      const stored = localStorage.getItem(key);
      let breaches = 0;
      if (stored) {
        const parsed = parseInt(stored, 10);
        breaches = Number.isNaN(parsed) ? 0 : parsed;
      }
      breaches += 1;
      localStorage.setItem(key, breaches.toString());
      if (breaches >= 5) {
        triggerBlacklist();
        setIsBlacklisted(true);
        localStorage.setItem(key, '0');
      }
      attemptAutonomousImprovement('Decoy breach detected. Rotating defensive signatures.');
    };

    const handleBlacklist = () => {
      setIsBlacklisted(true);
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('security-alert', handleSecurityAlert);
      window.addEventListener('sentinel-shadow-recorded', handleShadowRecorded);
      window.addEventListener('sentinel-decoy-breach', handleDecoyBreach);
      window.addEventListener('sentinel-blacklist', handleBlacklist);
      return () => {
        window.removeEventListener('security-alert', handleSecurityAlert);
        window.removeEventListener('sentinel-shadow-recorded', handleShadowRecorded);
        window.removeEventListener('sentinel-decoy-breach', handleDecoyBreach);
        window.removeEventListener('sentinel-blacklist', handleBlacklist);
      };
    }
  }, [attemptAutonomousImprovement, isLockdown, triggerLockdown, rotateDecoys, triggerBlacklist]);

  return { cyclesRun, isImproving, level, isLockdown, isBlacklisted };
};
