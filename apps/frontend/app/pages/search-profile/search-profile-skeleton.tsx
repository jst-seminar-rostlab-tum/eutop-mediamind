import { Skeleton } from "~/components/ui/skeleton";

export function SearchProfileSkeleton() {
  return (
    <>
      <div className="my-8">
        <Skeleton className="h-4 w-[15%] mb-2" />
        <div className="flex justify-start items-center gap-4">
          <Skeleton className="h-10 w-[20%] rounded-md" />
          <Skeleton className="h-6 w-[8%]" />
          <Skeleton className="h-6 w-[10%]" />
          <Skeleton className="h-6 w-[10%]" />
        </div>
      </div>
      <div className="grid grid-cols-6 gap-8 mt-10">
        {/* Sidebar skeleton */}
        <div className="col-span-2 space-y-6 mt-2">
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
        <div className="col-span-4 space-y-6">
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
    </>
  );
}
