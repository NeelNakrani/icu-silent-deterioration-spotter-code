import React from 'react';
import { useLocalStorage } from './useLocalStorage';
import type { TweakValue, TweakEdits } from '../types/icu';

export function useTweaks<T extends Record<string, TweakValue>>(defaults: T): [T, (keyOrEdits: keyof T | Partial<T>, val?: TweakValue) => void] {
  const [values, setValues] = useLocalStorage<T>('icu-tweaks', defaults);
  const setTweak = React.useCallback((keyOrEdits: keyof T | Partial<T>, val?: TweakValue) => {
    const edits = typeof keyOrEdits === 'object' && keyOrEdits !== null
      ? (keyOrEdits as TweakEdits) : { [keyOrEdits as string]: val } as TweakEdits;
    setValues({ ...values, ...edits } as T);
    window.parent.postMessage({ type: '__edit_mode_set_keys', edits }, '*');
  }, [values, setValues]);
  return [values, setTweak];
}
