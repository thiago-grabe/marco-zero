import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { contractsApi, type ContractCreate } from "@/lib/api/client";
import { useContractStore } from "@/stores/contract";
import { isAuthenticated } from "@/lib/auth";

export function useContracts() {
  return useQuery({
    queryKey: ["contracts"],
    queryFn: contractsApi.list,
    enabled: isAuthenticated(),
    retry: false,
  });
}

export function useContract(id: string | null) {
  return useQuery({
    queryKey: ["contracts", id],
    queryFn: () => contractsApi.get(id!),
    enabled: !!id && isAuthenticated(),
    retry: false,
  });
}

export function useCreateContract() {
  const queryClient = useQueryClient();
  const setActiveContractId = useContractStore((s) => s.setActiveContractId);

  return useMutation({
    mutationFn: (body: ContractCreate) => contractsApi.create(body),
    onSuccess: (contract) => {
      queryClient.invalidateQueries({ queryKey: ["contracts"] });
      setActiveContractId(contract.id);
    },
  });
}

export function useActiveContract() {
  const activeId = useContractStore((s) => s.activeContractId);
  return useContract(activeId);
}
