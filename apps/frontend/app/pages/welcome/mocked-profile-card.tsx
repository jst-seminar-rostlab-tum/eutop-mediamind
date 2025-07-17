import {
  Trash2,
  SquarePen,
  MoreVertical,
  ChevronRight,
  FileText,
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Button } from "~/components/ui/button";
import type { Profile } from "../../../types/model";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { useTranslation } from "react-i18next";
import { RoleBadge } from "~/custom-components/dashboard/role-badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "~/components/ui/tooltip";
import { toast } from "sonner";

interface ProfileCardProps {
  profile: Profile;
  profile_id: string;
}

export function MockedProfileCard({ profile, profile_id }: ProfileCardProps) {
  const [isTruncated, setIsTruncated] = useState(false);
  const titleRef = useRef<HTMLHeadingElement>(null);

  const { t } = useTranslation();

  useEffect(() => {
    const element = titleRef.current;
    const handleResize = () => {
      if (element) {
        setIsTruncated(element.scrollWidth > element.clientWidth);
      }
    };

    handleResize();
    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, [profile.name]);

  const getRoleBadge = () => {
    if (profile.owner_id === profile_id) {
      return <RoleBadge variant={"owner"} />;
    } else if (profile.can_edit_user_ids.includes(profile_id)) {
      return <RoleBadge variant={"editor"} />;
    } else if (profile.can_read_user_ids.includes(profile_id)) {
      return <RoleBadge variant={"reader"} />;
    }
    return null;
  };

  const getVisibilityBadge = () => {
    if (profile.is_public) {
      return <RoleBadge variant={"public"} />;
    }

    const totalUsersWithAccess = new Set([
      ...profile.can_read_user_ids,
      ...profile.can_edit_user_ids,
    ]).size;

    if (
      totalUsersWithAccess === 0 ||
      (totalUsersWithAccess === 1 && profile.owner_id === profile_id)
    ) {
      return <RoleBadge variant={"private"} />;
    }

    return <RoleBadge variant={"shared"} />;
  };

  const totalKeywords = profile.topics.flatMap(
    (topic) => topic.keywords,
  ).length;

  return (
    <TooltipProvider>
      <div className="w-[15.5rem] h-[14rem] rounded-3xl shadow-[2px_2px_15px_rgba(0,0,0,0.1)] p-5 ">
        <div className="h-full flex-1 flex flex-col justify-between overflow-hidden">
          <div>
            <div className={"flex justify-between"}>
              <div className={"flex items-center gap-2"}>
                <Tooltip open={isTruncated ? undefined : false}>
                  <TooltipTrigger asChild>
                    <h2
                      ref={titleRef}
                      className={`font-semibold text-xl min-w-0 flex-1 truncate ${
                        profile.new_articles_count > 0
                          ? "max-w-[140px]"
                          : "max-w-[160px]"
                      }`}
                    >
                      {profile.name}
                    </h2>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{profile.name}</p>
                  </TooltipContent>
                </Tooltip>
                {profile.new_articles_count > 0 && (
                  <span
                    className={`bg-red-200 ${profile.new_articles_count > 99 ? "w-8" : "w-5"} h-5 rounded-full flex items-center justify-center text-sm font-bold text-red-900`}
                  >
                    {profile.new_articles_count}
                  </span>
                )}
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="secondary" className="h-8 w-8 p-0 ">
                    <span className="sr-only">{t("sr-only.open_menu")}</span>
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="center">
                  <DropdownMenuItem
                    onClick={() =>
                      toast.info(t("landing_page.edit_profile_toast"))
                    }
                  >
                    <SquarePen className="text-primary" />
                    {t("Edit")}
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => toast.info(t("landing_page.reports_toast"))}
                  >
                    <FileText className="text-primary" />
                    {t("search_profile.reports")}
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() =>
                      toast.info(t("landing_page.delete_profile_toast"))
                    }
                    className="text-red-500 focus:text-red-500"
                  >
                    <Trash2 className="text-red-500" />
                    {t("Delete")}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <div className={"flex gap-2 flex-wrap"}>
              {getRoleBadge()}
              {getVisibilityBadge()}
            </div>
            <div className={"mt-2 mb-2"}>
              <div className={"flex items-center gap-1"}>
                <div className="bg-gray-100 px-1 py-0.5 text-sm rounded-sm text-gray-700 flex gap-1">
                  <span className={"font-bold"}>{profile.topics.length}</span>
                  {t("search_profile.Topics")}
                </div>
                <div className="bg-gray-100 px-1 py-0.5 text-sm rounded-sm text-gray-700 flex gap-1">
                  <span className={"font-bold"}>{totalKeywords}</span>
                  {t("search_profile.Keywords")}
                </div>
              </div>
            </div>
          </div>
          <div
            onClick={() => toast.info(t("landing_page.checkout_sp_toast"))}
            className="w-full h-20 bg-gray-100 items-center flex justify-center rounded-2xl hover:bg-gray-200 hover:cursor-pointer transition-background duration-300"
          >
            <span className={"text-gray-700"}>
              {t("search_profile.Explore")}
            </span>
            <ChevronRight className="w-7 h-7" />
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}
