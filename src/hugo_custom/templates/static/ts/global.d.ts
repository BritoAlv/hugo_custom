declare function renderMathInElement(
  element: Element,
  options?: {
    delimiters?: Array<{ left: string; right: string; display: boolean }>;
    throwOnError?: boolean;
    [key: string]: unknown;
  }
): void;

declare namespace echarts {
  interface ECharts {
    setOption(option: unknown, opts?: { notMerge?: boolean }): void;
    on(event: string, handler: (params: unknown) => void): void;
    resize(): void;
    dispose(): void;
  }
  function init(el: HTMLElement): ECharts;
}