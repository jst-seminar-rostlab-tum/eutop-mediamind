import { Skeleton } from "~/components/ui/skeleton";

export function BreakingNewsCardSkeleton() {
  return (
    <div className="border p-3 w-full rounded-3xl flex gap-4">
      <div className="overflow-hidden rounded-2xl w-27 h-28 flex-shrink-0">
        <Skeleton className="w-full h-full" />
      </div>

      <div className="flex-1">
        <div>
          <Skeleton className="h-7 w-3/4 mb-2" />
        </div>

        <div className="flex-grow text-gray-600">
          <Skeleton className="h-4 w-24 mb-1" />

          <div className="mb-2 space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </div>

          <div className="flex gap-4">
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-8 w-20" />
          </div>
        </div>
      </div>
    </div>
  );
}
