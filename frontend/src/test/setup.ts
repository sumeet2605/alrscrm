import "@testing-library/jest-dom/vitest";

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false
  })
});

const originalQuerySelectorAll = Element.prototype.querySelectorAll;
Element.prototype.querySelectorAll = function patchedQuerySelectorAll(selectors: string) {
  try {
    return originalQuerySelectorAll.call(this, selectors);
  } catch (error) {
    if (error instanceof DOMException && error.name === "SyntaxError") {
      return document.createDocumentFragment().querySelectorAll("*");
    }
    throw error;
  }
};

const originalGetComputedStyle = window.getComputedStyle;
window.getComputedStyle = (element: Element, pseudoElement?: string | null) => {
  if (pseudoElement) {
    return originalGetComputedStyle(element);
  }
  return originalGetComputedStyle(element);
};
