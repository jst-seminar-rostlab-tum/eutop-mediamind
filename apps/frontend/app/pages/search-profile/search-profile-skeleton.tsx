import { Skeleton } from "~/components/ui/skeleton";

export function SearchProfileSkeleton() {
  return (
    <div className="flex flex-col w-full justify-center items-center">
      {/* Header skeleton */}
      <div className="my-8 w-full">
        <Skeleton className="h-4 w-[15%] mb-3" />
        <div className="flex flex-row justify-between">
          <div className="w-full flex justify-start items-center gap-4">
            <Skeleton className="h-10 w-[20%] rounded-md" />
            <Skeleton className="h-6 w-[8%]" />
            <Skeleton className="h-6 w-[10%]" />
            <Skeleton className="h-6 w-[10%]" />
          </div>
          <Skeleton className="h-6 w-[10%]" />
        </div>
      </div>
      <div className="flex gap-8 w-full justify-start">
        {/* Sidebar skeleton */}
        <div className="space-y-6 mt-2 max-w-[400px] flex-grow">
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-10 w-full rounded-md mb-8" />

          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-8 w-full rounded-md" />
          <Skeleton className="h-30 w-full rounded-md mb-8" />

          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-8 w-full rounded-md" />
          <Skeleton className="h-30 w-full rounded-md mb-8" />

          <Skeleton className="h-6 w-32" />
          <div className="flex gap-2">
            <Skeleton className="h-10 w-full rounded-md" />
            <Skeleton className="h-10 w-full rounded-md" />
          </div>
        </div>

        {/* Content skeleton */}
        <div className="space-y-6 flex-grow">
          <Skeleton className="h-10 w-full rounded-md" />
          {[...Array(4)].map((_, i) => (
            <div key={i} className="p-4 border rounded-lg space-y-3">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <div className="flex gap-2 mt-2">
                <Skeleton className="h-6 w-24 rounded-lg" />
                <Skeleton className="h-6 w-32 rounded-lg" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ArticlesSkeleton() {
  return (
    <div className="space-y-6 flex-grow">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="p-4 border rounded-xl space-y-3">
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="flex gap-2 mt-2">
            <Skeleton className="h-6 w-24 rounded-lg" />
            <Skeleton className="h-6 w-32 rounded-lg" />
          </div>
        </div>
      ))}
    </div>
  );
}
