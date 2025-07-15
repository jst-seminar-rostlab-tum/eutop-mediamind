import {
  Trash2,
  SquarePen,
  OctagonAlert,
  MoreVertical,
  ChevronRight,
  Loader2,
  FileText,
} from "lucide-react";
import type { KeyedMutator } from "swr";
import { useState, useRef, useEffect } from "react";

import { Button } from "~/components/ui/button";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import type { Profile } from "../../../types/model";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "~/components/ui/alert-dialog";
import { useTranslation } from "react-i18next";
import { RoleBadge } from "~/custom-components/dashboard/role-badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "~/components/ui/tooltip";
import { Link } from "react-router";
import { client } from "types/api";
import { toast } from "sonner";

interface ProfileCardProps {
  profile: Profile;
  mutateDashboard: KeyedMutator<Profile[]>;
  profile_id: string;
}

export function ProfileCard({
  profile,
  mutateDashboard,
  profile_id,
}: ProfileCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
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

  const deleteProfile = async () => {
    try {
      setIsDeleting(true);
      await client.DELETE("/api/v1/search-profiles/{search_profile_id}", {
        params: { path: { search_profile_id: profile.id } },
      });
      mutateDashboard(
        (profiles) => profiles?.filter((p) => p.id !== profile.id) || [],
      );
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error) {
      toast.error(t("search_profile.delete_error"));
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
      toast.success(t("search_profile.delete_success"));
    }
  };

  const totalKeywords = profile.topics.flatMap(
    (topic) => topic.keywords,
  ).length;

  return (
    <TooltipProvider>
      <div className="w-[15.5rem] h-[14rem] rounded-xl shadow-[2px_2px_15px_rgba(0,0,0,0.1)] p-5 ">
        <div className="h-full flex-1 flex flex-col justify-between">
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
              <EditProfile
                profile={profile}
                dialogOpen={showEditDialog}
                setDialogOpen={setShowEditDialog}
                mutateDashboard={mutateDashboard}
              />
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-8 w-8 p-0 ">
                    <span className="sr-only">{t("sr-only.open_menu")}</span>
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setShowEditDialog(true)}>
                    <SquarePen className="text-primary" />
                    {t("Edit")}
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to={`/search-profile/${profile.id}/reports`}>
                      <FileText className="text-primary" />
                      {t("search_profile.reports")}
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => {
                      setShowDeleteDialog(true);
                    }}
                    className="text-destructive focus:text-destructive"
                  >
                    <Trash2 className="text-destructive" />
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
          <Link
            to={`/search-profile/${profile.id}`}
            className="w-full h-10 mt-10 bg-gray-100 items-center flex justify-center rounded-lg hover:bg-accent transition-background duration-300"
          >
            <span className={"text-gray-700"}>
              {t("search_profile.Explore")}
            </span>
            <ChevronRight className="size-5" />
          </Link>
        </div>
      </div>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center">
              <OctagonAlert size={20} className="text-destructive mr-2" />
              {t("confirmation_dialog.title")}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {t("confirmation_dialog.delete_text")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("Back")}</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => deleteProfile()}
            >
              {isDeleting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Trash2 />
              )}
              {t("Delete")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </TooltipProvider>
  );
}
