import type {
  ComponentType,
  HTMLAttributes,
  JSX,
  PropsWithChildren,
} from "react";

interface Props {
  hierachy?: number; // headline level, if none specified normal text
  tag?: ComponentType<HTMLAttributes<HTMLElement>>;
}

/*
Component to handle Text in the app consistent. Lets develop this component on the fly an add new hierachy levels once we need them.
Check out https://ui.shadcn.com/docs/components/typography for a guide on typography (in code view you can copy the css classes from shadcn)
*/
export default function Text({
  tag,
  hierachy,
  children,
}: PropsWithChildren<Props>): JSX.Element {
  if (hierachy == 1) {
    // For first level headlines
    const Tag = tag || "h1";
    return (
      <Tag className="text-4xl font-extrabold tracking-tight lg:text-5xl">
        {children}
      </Tag>
    );
  }

  // TODO: add other headline levels

  // Normal Text
  return <p className="leading-7 [&:not(:first-child)]:mt-6">{children}</p>;
}
