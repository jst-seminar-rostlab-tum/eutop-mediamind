import type { HTMLAttributes, JSX, PropsWithChildren } from "react";

export default function Layout({
  children,
  className,
}: PropsWithChildren & HTMLAttributes<HTMLDivElement>): JSX.Element {
  return (
    <main
      className={`${className} mx-auto w-full max-w-4xl  xl:max-w-7xl pt-8`}
    >
      {children}
    </main>
  );
}
