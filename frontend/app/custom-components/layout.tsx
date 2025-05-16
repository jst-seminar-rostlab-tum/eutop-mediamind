import type { HTMLAttributes, JSX, PropsWithChildren } from "react";

export default function Layout({
  children,
  className,
}: PropsWithChildren & HTMLAttributes<HTMLDivElement>): JSX.Element {
  return (
    <main
      className={`${className} mx-auto grid w-full max-w-2xl grid-cols-1 gap-10 xl:max-w-5xl`}
    >
      {children}
    </main>
  );
}
