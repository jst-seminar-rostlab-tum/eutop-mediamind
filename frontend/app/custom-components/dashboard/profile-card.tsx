import {
  Rocket,
  MoreHorizontal,
  Trash2,
  SquarePen,
  OctagonAlert,
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

interface ProfileCardProps {
  profile: Profile;
  dialogOpen: boolean;
  setDialogOpen: (value: boolean) => void;
  mutateDashboard: KeyedMutator<Profile[]>;
}

export function ProfileCard({
  profile,
  dialogOpen,
  setDialogOpen,
  mutateDashboard,
}: ProfileCardProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  return (
    <>
      <Card className="w-[15rem] h-[14rem] rounded-3xl shadow-[2px_2px_15px_rgba(0,0,0,0.1)] hover:shadow-none transition-shadow duration-300 ease-in-out">
        <CardHeader className="-mt-2">
          <div className={"flex justify-between"}>
            <div>
              <CardTitle className="font-semibold text-xl">
                {profile.name}
              </CardTitle>
            </div>
            <EditProfile
              profile={profile}
              dialogOpen={dialogOpen}
              setDialogOpen={setDialogOpen}
              mutateDashboard={mutateDashboard}
            />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 w-8 p-0">
                  <span className="sr-only">Open menu</span>
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="center">
                <DropdownMenuItem onClick={() => setDialogOpen(true)}>
                  <SquarePen className="text-primary" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    setShowDeleteDialog(true);
                  }}
                  className="text-red-500 focus:text-red-500"
                >
                  <Trash2 className="text-red-500" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="flex items-center gap-2">
            <Rocket className={"h-4 w-4"} />
            <span className="font-semibold text-sm">{0} new articles!</span>
          </div>
        </CardHeader>
        <CardContent className="-mt-4">
          <div className="w-full h-[112px] overflow-hidden rounded-[38px]">
            <img
              src={
                "https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png"
              }
              alt=""
              className="h-full w-full object-cover object-center"
            />
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center">
              <OctagonAlert size={20} className="text-red-500 mr-2" />
              Are you sure?
            </AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this search profile
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Back</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => {
                setShowDeleteDialog(false);
                console.log("Delete: ", profile.name);
                //call delete endpoint here
              }}
            >
              <Trash2 />
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
