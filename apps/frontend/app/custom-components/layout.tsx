import type { HTMLAttributes, JSX, PropsWithChildren } from "react";

export default function Layout({
  children,
  className,
}: PropsWithChildren & HTMLAttributes<HTMLDivElement>): JSX.Element {
  return (
    <main
      className={`${className} mx-auto w-full max-w-10/12 xl:max-w-11/12 pt-8`}
    >
      {children}
    </main>
  );
}
