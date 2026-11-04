import { create } from "zustand";
import type { PoemCard } from "../../types";

interface PoemState {
  currentPoem: PoemCard | null;
  collection: PoemCard[];
  setCurrentPoem: (poem: PoemCard, collection?: PoemCard[]) => void;
}

export const usePoemStore = create<PoemState>((set) => ({
  currentPoem: null,
  collection: [],
  setCurrentPoem: (poem, collection = []) => set({ currentPoem: poem, collection }),
}));
