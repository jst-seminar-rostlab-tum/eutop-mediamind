import {
  Rocket,
  Trash2,
  SquarePen,
  OctagonAlert,
  MoreVertical,
  UserSearch,
  MoveRight,
} from "lucide-react";
import type { KeyedMutator } from "swr";

import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import type { Profile } from "../../../types/model";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "~/components/ui/dropdown-menu";
import { useState } from "react";
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
import { useNavigate } from "react-router";

interface ProfileCardProps {
  profile: Profile;
  mutateDashboard: KeyedMutator<Profile[]>;
}

export function ProfileCard({ profile, mutateDashboard }: ProfileCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);

  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <>
      <Card className="w-[15rem] rounded-2xl shadow-[2px_2px_15px_rgba(0,0,0,0.1)] transition-shadow duration-300 ease-in-out">
        <CardHeader className="-mt-2">
          <div className={"flex justify-between"}>
            <div>
              <CardTitle className="font-semibold text-xl">
                {profile.name}
              </CardTitle>
            </div>
            <EditProfile
              profile={profile}
              dialogOpen={showEditDialog}
              setDialogOpen={setShowEditDialog}
              mutateDashboard={mutateDashboard}
            />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center">
                <DropdownMenuItem onClick={() => setShowEditDialog(true)}>
                  <SquarePen className="text-primary" />
                  {t("edit")}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    setShowDeleteDialog(true);
                  }}
                  className="text-red-500 focus:text-red-500"
                >
                  <Trash2 className="text-red-500" />
                  {t("delete")}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="flex items-center gap-2">
            <Rocket className={"h-4 w-4"} />
            <span className="font-semibold text-sm">
              {Math.floor(Math.random() * 20)}
              {" " + t("new_articles")}
            </span>
          </div>
        </CardHeader>
        <CardContent className="">
          <div className="flex justify-center">
            <Button
              variant={"outline"}
              onClick={() => navigate(`/search-profile/${profile.id}`)}
            >
              <UserSearch />
              Go to Profile
              <MoveRight />
            </Button>
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center">
              <OctagonAlert size={20} className="text-red-500 mr-2" />
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
              onClick={() => {
                setShowDeleteDialog(false);
                console.log("Delete: ", profile.name);
                //call delete endpoint here
              }}
            >
              <Trash2 />
              {t("Delete")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
