declare function renderMathInElement(
  element: Element,
  options?: {
    delimiters?: Array<{ left: string; right: string; display: boolean }>;
    throwOnError?: boolean;
    [key: string]: unknown;
  }
): void;