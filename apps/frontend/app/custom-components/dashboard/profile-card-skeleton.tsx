import { Skeleton } from "~/components/ui/skeleton";

export function ProfileCardSkeleton() {
  return (
    <div className="p-6 bg-white border rounded-xl shadow-sm animate-pulse">
      <div className="flex justify-between items-center mb-4">
        <Skeleton className="h-6 w-20" />
        <div className="flex space-x-2">
          <Skeleton className="h-5 w-14 rounded-full" />
          <Skeleton className="h-5 w-14 rounded-full" />
        </div>
      </div>

      <div className="flex items-center space-x-4 mb-6">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-24" />
      </div>

      <Skeleton className="h-10 w-full rounded-lg" />
    </div>
  );
}
