import { useState, useMemo } from "react";
import { cloneDeep, isEqual } from "lodash-es";
import type { KeyedMutator } from "swr";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";

import {
  Book,
  Mail,
  Newspaper,
  Settings,
  Edit2,
  Check,
  X,
  OctagonAlert,
  LogOut,
} from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Topics } from "~/custom-components/profile/edit/topics";
import { Mailing } from "~/custom-components/profile/edit/mailing";
import { Subscriptions } from "~/custom-components/profile/edit/subscriptions";
import { ScrollArea } from "~/components/ui/scroll-area";
import { General } from "~/custom-components/profile/edit/general";
import { client } from "../../../../types/api";
import { useAuthorization } from "~/hooks/use-authorization";
import type { Profile } from "../../../../types/model";
import { toast } from "sonner";
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

interface EditProfileProps {
  profile?: Profile;
  dialogOpen: boolean;
  setDialogOpen: (value: boolean) => void;
  mutateDashboard: KeyedMutator<Profile[]>;
}

export function EditProfile({
  profile,
  dialogOpen,
  setDialogOpen,
  mutateDashboard,
}: EditProfileProps) {
  const isCreating = !profile;

  const { user } = useAuthorization();
  const { t } = useTranslation();

  const initialProfile: Profile = {
    id: "",
    name: "",
    is_public: false,
    organization_emails: [],
    profile_emails: [],
    subscriptions: [],
    topics: [],
    can_edit_user_ids: [],
    can_read_user_ids: [],
    owner_id: user?.id ?? "",
    is_owner: true,
    is_reader: true,
    is_editor: true,
    new_articles_count: 0,
    language: user?.language ?? "en",
  };

  const [showCancelDialog, setShowCancelDialog] = useState(false);

  const [isEditingName, setIsEditingName] = useState(isCreating);

  const [editedProfile, setEditedProfile] = useState<Profile>(
    cloneDeep(profile ?? initialProfile),
  );
  const [profileName, setProfileName] = useState(editedProfile.name || "");

  const [isSaving, setIsSaving] = useState(false);

  const handleNameSave = () => {
    if (isCreating && !profileName.trim()) {
      toast.error("Profile name is required");
      return;
    }
    setIsEditingName(false);
    setEditedProfile({ ...editedProfile, name: profileName });
  };

  const handleNameCancel = () => {
    setProfileName(editedProfile.name);
    setIsEditingName(false);
  };

  const isValid = useMemo(
    () =>
      (isCreating
        ? !isEqual(initialProfile, editedProfile)
        : !isEqual(profile, editedProfile)) &&
      editedProfile.name.trim().length > 0 &&
      !isEditingName,
    [isCreating, profileName, initialProfile, profile, editedProfile],
  );

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const requestData = {
        name: editedProfile.name,
        is_public: editedProfile.is_public,
        organization_emails: editedProfile.organization_emails,
        profile_emails: editedProfile.profile_emails,
        can_read_user_ids: editedProfile.can_read_user_ids,
        can_edit_user_ids: editedProfile.can_edit_user_ids,
        subscriptions: editedProfile.subscriptions,
        topics: editedProfile.topics,
        owner_id: editedProfile.owner_id,
        language: editedProfile.language,
      };

      if (isCreating) {
        const result = await client.POST("/api/v1/search-profiles", {
          body: requestData,
        });
        if (result.error) {
          throw new Error(result.error as string);
        }
        mutateDashboard(
          (profiles) =>
            [result.data as Profile, ...(profiles ?? [])].filter(Boolean),
          { revalidate: false },
        );
        toast.success("Profile created successfully", {
          description: "Your new profile has been created.",
        });
      } else {
        const result = await client.PUT(
          "/api/v1/search-profiles/{search_profile_id}",
          {
            params: { path: { search_profile_id: profile!.id } },
            body: requestData,
          },
        );
        if (result.error) {
          throw new Error(result.error as string);
        }
        mutateDashboard(
          (profiles) => {
            const filteredProfiles =
              profiles?.filter((p) => p.id !== profile!.id) ?? [];
            return [result.data as Profile, ...filteredProfiles].filter(
              Boolean,
            );
          },
          { revalidate: false },
        );
        toast.success("Profile updated successfully", {
          description: "Your changes have been saved.",
        });
      }
    } catch (error) {
      console.error(error);
      toast.error(`Profile ${isCreating ? "creation" : "update"} failed`, {
        description: `Your ${isCreating ? "new profile has not been created" : "changes have not been saved"}.`,
      });
    } finally {
      setIsSaving(false);
      // reset component state
      if (isCreating) {
        handleCancel();
      } else {
        setDialogOpen(false);
      }
    }
  };

  const handleCancel = () => {
    setEditedProfile(cloneDeep(profile ?? initialProfile));
    setProfileName(profile?.name || "");
    setIsEditingName(isCreating);
    setDialogOpen(false);
  };

  return (
    <>
      <Dialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open && isValid) {
            // prevent closing and show confirmation
            setShowCancelDialog(true);
          } else {
            handleCancel();
          }
        }}
      >
        <DialogContent
          className={"flex flex-col gap-8 min-w-1/2 rounded-3xl h-3/4"}
        >
          <DialogHeader className="flex-none">
            <div className={"flex items-center gap-3"}>
              {isEditingName ? (
                <div className="flex items-center gap-2 flex-1">
                  <DialogTitle className="text-xl font-semibold">
                    {isCreating
                      ? t("edit_profile.create")
                      : t("edit_profile.edit")}
                  </DialogTitle>
                  <Input
                    value={profileName ?? ""}
                    placeholder={t("edit_profile.profile_name")}
                    onChange={(e) => setProfileName(e.target.value)}
                    className="flex-1 max-w-xs"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleNameSave();
                      if (e.key === "Escape") handleNameCancel();
                    }}
                  />
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleNameSave}
                    className="h-8 w-8 p-0"
                  >
                    <Check className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleNameCancel}
                    className="h-8 w-8 p-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-2 w-full">
                  <DialogTitle className={"text-xl break-all"}>
                    {isCreating
                      ? t("edit_profile.create")
                      : t("edit_profile.edit")}
                    {profileName || "New Profile"}
                  </DialogTitle>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setIsEditingName(true)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
          </DialogHeader>

          <Tabs
            defaultValue="general"
            className="flex flex-col overflow-hidden w-full grow"
          >
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="general" className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                <span>{t("edit_profile.general")}</span>
              </TabsTrigger>
              <TabsTrigger value="topics" className="flex items-center gap-2">
                <Book className="h-5 w-5" />
                <span>{t("edit_profile.topics")}</span>
              </TabsTrigger>
              <TabsTrigger value="mailing" className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                <span>{t("edit_profile.mailing")}</span>
              </TabsTrigger>
              <TabsTrigger
                value="subscriptions"
                className="flex items-center gap-2"
              >
                <Newspaper className="h-5 w-5" />
                <span>{t("edit_profile.subscriptions")}</span>
              </TabsTrigger>
            </TabsList>
            <div className="grow overflow-hidden">
              <ScrollArea className="h-full pr-4">
                <TabsContent value="general">
                  <General
                    profile={editedProfile}
                    setProfile={setEditedProfile}
                  />
                </TabsContent>

                <TabsContent value="topics">
                  <Topics
                    profile={editedProfile}
                    setProfile={setEditedProfile}
                  />
                </TabsContent>

                <TabsContent value="mailing">
                  <Mailing
                    profile={editedProfile}
                    setProfile={setEditedProfile}
                  />
                </TabsContent>

                <TabsContent value="subscriptions">
                  <Subscriptions
                    profile={editedProfile}
                    setProfile={setEditedProfile}
                  />
                </TabsContent>
              </ScrollArea>
            </div>
          </Tabs>

          <div className="flex flex-none justify-end">
            <Button type="button" disabled={!isValid} onClick={handleSave}>
              {isSaving
                ? isCreating
                  ? t("edit_profile.creating")
                  : t("edit_profile.saving")
                : isCreating
                  ? t("edit_profile.save_create")
                  : t("edit_profile.save_changes")}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <AlertDialog open={showCancelDialog} onOpenChange={setShowCancelDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center">
              <OctagonAlert size={20} className="text-red-500 mr-2" />
              {t("confirmation_dialog.title")}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {t("confirmation_dialog.leave_text")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t("Back")}</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60"
              onClick={() => {
                handleCancel();
                setShowCancelDialog(false);
              }}
            >
              <LogOut className="text-white" />
              {t("Leave")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
