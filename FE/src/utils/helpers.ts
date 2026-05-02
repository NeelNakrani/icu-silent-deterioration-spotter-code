// Helper utility functions
export const formatDate = (date: Date | string): string => {
  return new Date(date).toLocaleDateString();
};

export const formatTime = (date: Date | string): string => {
  return new Date(date).toLocaleTimeString();
};

export const formatDateTime = (date: Date | string): string => {
  return new Date(date).toLocaleString();
};

export const debounce = <T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

export const throttle = <T extends (...args: unknown[]) => unknown>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), delay);
    }
  };
};

// Made with Bob
