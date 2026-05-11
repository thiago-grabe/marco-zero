import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ContractStore {
  activeContractId: string | null;
  setActiveContractId: (id: string | null) => void;
}

export const useContractStore = create<ContractStore>()(
  persist(
    (set) => ({
      activeContractId: null,
      setActiveContractId: (id) => set({ activeContractId: id }),
    }),
    { name: "mz-active-contract" }
  )
);
