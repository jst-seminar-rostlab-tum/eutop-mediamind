import { DashboardPage } from "~/pages/dashboard/dashboard";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
const queryClient = new QueryClient()

export default function DashboardRoute(){
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardPage />
    </QueryClientProvider>
  )
}