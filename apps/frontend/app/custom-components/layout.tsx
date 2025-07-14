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
        className={`mx-auto w-full max-w-10/12 xl:max-w-11/12 ${noOverflow ? "overflow-hidden grow flex flex-col" : ""}`}
      >
        {children}
      </div>
    </main>
  );
}
