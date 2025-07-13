import { Skeleton } from "~/components/ui/skeleton";

export function ReportCardSkeleton() {
  return (
    <div className="shadow-lg rounded-2xl p-4 h-40 w-50 space-y-1 flex flex-col justify-between">
      <div className="flex items-center gap-2">
        <Skeleton className="w-6 h-6" />
        <div className="flex items-baseline space-x-2">
          <Skeleton className="h-8 w-8" />
          <div className="flex space-x-1">
            <Skeleton className="h-4 w-12" />
            <Skeleton className="h-4 w-12" />
          </div>
        </div>
      </div>

      <div className="flex gap-2 items-center">
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-20" />
      </div>

      <Skeleton className="h-10 w-full" />
    </div>
  );
}
