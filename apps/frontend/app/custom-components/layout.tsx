import type { HTMLAttributes, JSX, PropsWithChildren } from "react";
import { cn } from "~/lib/utils";

export default function Layout({
  children,
  className,
  noOverflow = false,
}: PropsWithChildren &
  HTMLAttributes<HTMLDivElement> & { noOverflow?: boolean }): JSX.Element {
  return (
    <main
      className={cn(
        ` pt-8 grow flex flex-col ${noOverflow ? "overflow-hidden" : "overflow-auto"}`,
        className,
      )}
    >
      <div
        className={`mx-auto w-full max-w-8/12 xl:max-w-10/12 2xl:max-w-9/12 ${noOverflow ? "overflow-hidden grow flex flex-col" : ""}`}
      >
        {children}
      </div>
    </main>
  );
}
