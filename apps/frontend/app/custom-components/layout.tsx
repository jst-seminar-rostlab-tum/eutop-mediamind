import type { HTMLAttributes, JSX, PropsWithChildren } from "react";

export default function Layout({
  children,
  className,
}: PropsWithChildren & HTMLAttributes<HTMLDivElement>): JSX.Element {
  return (
    <main
      className={`${className} mx-auto w-full max-w-8/12 xl:max-w-10/12 2xl:max-w-9/12 pt-8`}
    >
      {children}
    </main>
  );
}
