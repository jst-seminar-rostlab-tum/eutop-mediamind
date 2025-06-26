import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import {
  Eye,
  EyeOff,
  UserCheck,
  UserPen,
  UserRoundCog,
  Users,
} from "lucide-react";

import { cn } from "~/lib/utils";

const roleBadgeVariants = cva(
  "inline-flex items-center gap-1 rounded-md transition-colors px-1.5 py-1 text-sm",
  {
    variants: {
      variant: {
        owner: "bg-purple-200 text-purple-900",
        reader: "bg-green-100 text-green-900",
        editor: "bg-blue-100 text-blue-900",
        public: "bg-indigo-100 text-indigo-900",
        shared: "bg-amber-100 text-amber-900",
        private: "bg-gray-100 text-gray-900",
      },
    },
  },
);

const roleConfig = {
  owner: {
    icon: UserRoundCog,
    label: "Owner",
  },
  reader: {
    icon: Eye,
    label: "Reader",
  },
  editor: {
    icon: UserPen,
    label: "Editor",
  },
  public: {
    icon: Users,
    label: "Public",
  },
  shared: {
    icon: UserCheck,
    label: "Shared",
  },
  private: {
    icon: EyeOff,
    label: "Private",
  },
} as const;

type RoleVariant = keyof typeof roleConfig;

interface RoleBadgeProps
  extends Omit<React.HTMLAttributes<HTMLDivElement>, "children">,
    VariantProps<typeof roleBadgeVariants> {
  variant: RoleVariant;
}

function RoleBadge({ className, variant, ...props }: RoleBadgeProps) {
  const config = roleConfig[variant];

  if (!config) {
    console.warn(`Role "${variant}" not found`);
    return null;
  }

  const { icon: Icon, label } = config;

  return (
    <div className={cn(roleBadgeVariants({ variant, className }))} {...props}>
      <Icon className={"h-4 w-4"} />
      <span>{label}</span>
    </div>
  );
}

export { RoleBadge, roleBadgeVariants, roleConfig, type RoleVariant };
