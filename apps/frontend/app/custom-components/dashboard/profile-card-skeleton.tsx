import { Skeleton } from "~/components/ui/skeleton";

export function ProfileCardSkeleton() {
  return (
    <div className="w-[15.5rem] h-[13rem] rounded-xl shadow-[2px_2px_15px_rgba(0,0,0,0.1)] p-5">
      <div className="h-full flex-1 flex flex-col justify-between">
        <div>
          <div className="flex justify-between">
            <Skeleton className="h-6 w-32" />
            <Skeleton className="h-8 w-8 rounded" />
          </div>

          <div className="flex gap-2 flex-wrap mb-2">
            <Skeleton className="h-7 w-14 rounded-sm" />
            <Skeleton className="h-7 w-16 rounded-sm" />
          </div>

          <div className="mt-2 mb-2">
            <div className="flex items-center gap-1">
              <Skeleton className="h-6 w-16 rounded-sm" />
              <Skeleton className="h-6 w-20 rounded-sm" />
            </div>
          </div>
        </div>

        <Skeleton className="w-full h-13 rounded-lg" />
      </div>
    </div>
  );
}
