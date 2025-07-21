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
        <div className="w-1/5 space-y-6 mt-2 flex-grow">
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
        <div className="w-4/5 space-y-2 flex-grow">
          <Skeleton className="h-10 w-full rounded-md" />
          <ArticlesSkeleton />
        </div>
      </div>
    </div>
  );
}
export function ArticlesSkeleton() {
  return (
    <div className="space-y-2 flex-grow">
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="mb-2 p-5 gap-4 justify-start border rounded-lg space-y-3" // Adjusted to mimic Card classes
        >
          <div className="flex flex-row gap-4">
            <Skeleton className="w-[120px] h-[120px] rounded-md shrink-0" />{" "}
            {/* Image skeleton */}
            <div className="flex flex-col justify-evenly space-y-2 flex-1">
              <Skeleton className="h-7 w-3/4" />{" "}
              {/* Title: taller to match text-xl */}
              <Skeleton className="h-4 w-full" /> {/* Summary line 1 */}
              <Skeleton className="h-4 w-5/6" /> {/* Summary line 2 */}
            </div>
          </div>
          <div className="flex gap-3 items-center flex-wrap">
            <Skeleton className="h-6 w-24 rounded-lg" /> {/* Relevance tag */}
            <Skeleton className="h-6 w-32 rounded-lg" /> {/* Topic tag 1 */}
            <Skeleton className="h-6 w-28 rounded-lg" /> {/* Topic tag 2 */}
            <Skeleton className="h-6 w-36 rounded-lg" />{" "}
            {/* Topic tag 3 or more */}
            <Skeleton className="h-6 w-40 rounded-lg" />{" "}
            {/* Show more button skeleton */}
          </div>
        </div>
      ))}
    </div>
  );
}
