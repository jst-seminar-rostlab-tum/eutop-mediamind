import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import {
  Crown,
  Eye,
  EyeOff, Globe, Moon, Sun, Sunrise,
  UserCheck,
  UserPen,
  UserRoundCog,
  Users,
} from "lucide-react";

import { cn } from "~/lib/utils";
import { useTranslation } from "react-i18next";

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
        ownership: "bg-blue-100 text-blue-900",
        visibility: "bg-blue-100 text-blue-900",
        de: "bg-purple-200 text-purple-900",
        en: "bg-blue-200 text-blue-900",
        morning: "border text-gray-900",
        afternoon: "border text-gray-900",
        evening: "border text-gray-900",
      },
    },
  },
);

const roleConfig = {
  owner: {
    icon: UserRoundCog,
    label: "role-badge.owner",
  },
  reader: {
    icon: Eye,
    label: "role-badge.reader",
  },
  editor: {
    icon: UserPen,
    label: "role-badge.editor",
  },
  public: {
    icon: Users,
    label: "role-badge.public",
  },
  shared: {
    icon: UserCheck,
    label: "role-badge.shared",
  },
  private: {
    icon: EyeOff,
    label: "role-badge.private",
  },
  ownership: {
    icon: Crown,
    label: "role-badge.ownership",
  },
  visibility: {
    icon: Eye,
    label: "role-badge.visibility",
  },
  de: {
    icon: Globe,
    label: "DE",
  },
  en: {
    icon: Globe,
    label: "EN",
  },
  morning: {
    icon: Sunrise,
    label: "Morning",
  },
  afternoon: {
    icon: Sun,
    label: "Afternoon",
  },
  evening: {
    icon: Moon,
    label: "Evening",
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
  const { t } = useTranslation();

  if (!config) {
    console.warn(`Role "${variant}" not found`);
    return null;
  }

  const { icon: Icon, label } = config;

  return (
    <div className={cn(roleBadgeVariants({ variant, className }))} {...props}>
      <Icon className={"h-4 w-4"} />
      <span>{t(label)}</span>
    </div>
  );
}

export { RoleBadge, roleBadgeVariants, roleConfig, type RoleVariant };
