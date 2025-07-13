import { Skeleton } from "~/components/ui/skeleton";

export function TableSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-9 w-[83%] rounded-md" />
        <Skeleton className="h-9 w-[15%] rounded-md" />
      </div>

      <div>
        <Skeleton className="h-9 w-[100%] rounded-md mb-2" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex justify-between py-2">
            <Skeleton className="h-5 w-[35%]" />
            <Skeleton className="h-5 w-[5%] mr-28" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function UserTableSkeleton() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-9 w-[83%] rounded-md" />
        <Skeleton className="h-9 w-[15%] rounded-md" />
      </div>

      <div>
        <Skeleton className="h-9 w-[100%] rounded-md mb-2" />
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex justify-between py-2">
            <Skeleton className="h-5 w-[35%]" />
            <Skeleton className="h-5 w-[35%]" />
            <Skeleton className="h-5 w-[15%]" />
            <Skeleton className="h-5 w-[5%] mr-4" />
          </div>
        ))}
      </div>
    </div>
  );
}
