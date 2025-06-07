import { useState } from "react";
import { cloneDeep, isEqual } from "lodash-es";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "~/components/ui/dialog";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";

import { Book, Mail, Newspaper, Settings, Edit2, Check, X } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Topics } from "~/custom-components/profile/edit/topics";
import { Mailing } from "~/custom-components/profile/edit/mailing";
import { Subscriptions } from "~/custom-components/profile/edit/subscriptions";
import { ScrollArea } from "~/components/ui/scroll-area";
import { General } from "~/custom-components/profile/edit/general";
import { client, useMutate } from "../../../../types/api";
import { useAuthorization } from "~/hooks/use-authorization";
import type { components } from "../../../../types/api-types-v1";

interface EditProfileProps {
  profile: components["schemas"]["SearchProfileDetailResponse"];
  trigger: React.ReactElement;
}

export function EditProfile({ profile, trigger }: EditProfileProps) {
  const [isEditingName, setIsEditingName] = useState(false);
  const [profileName, setProfileName] = useState(profile.name);
  const [editedProfile, setEditedProfile] = useState(cloneDeep(profile));

  const transformToUpdateRequest = (
    profile: components["schemas"]["SearchProfileDetailResponse"],
  ): components["schemas"]["SearchProfileUpdateRequest"] => {
    return {
      name: profile.name,
      public: profile.public,
      organization_emails: profile.organization_emails,
      profile_emails: profile.profile_emails,
      subscriptions: profile.subscriptions,
      topics: profile.topics,
    };
  };

  const handleNameSave = () => {
    setIsEditingName(false);
    setEditedProfile({ ...editedProfile, name: profileName });
  };

  const handleNameCancel = () => {
    setProfileName(editedProfile.name);
    setIsEditingName(false);
  };

  const [isSaving, setIsSaving] = useState(false);
  const { authorizationHeaders } = useAuthorization();
  const mutate = useMutate();

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updateRequest = transformToUpdateRequest(editedProfile);
      console.log(updateRequest);

      const response = await client.PUT(
        "/api/v1/search-profiles/{search_profile_id}",
        {
          params: { path: { search_profile_id: profile.id } },
          body: updateRequest,
          headers: authorizationHeaders,
        },
      );
      console.log(response);
      await mutate(["/api/v1/search-profiles"]);

      console.log("Profile updated successfully!");
    } catch (error) {
      console.error("Failed to update profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>

      <DialogContent className={"min-w-1/2 rounded-3xl max-h-3/4"}>
        <DialogHeader>
          <div className={"flex items-center gap-3"}>
            {isEditingName ? (
              <div className="flex items-center gap-2 flex-1">
                <span className="text-xl font-semibold">
                  {!profile.name ? "Create" : "Edit"} Profile:
                </span>
                <Input
                  value={profileName ?? ""}
                  placeholder="Profile name"
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
              <div className="flex items-center gap-2">
                <DialogTitle className={"text-xl"}>
                  {!profile.name ? "Create" : "Edit"} Profile: {profileName}
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

        <ScrollArea className="max-h-[60vh] pr-4">
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="general" className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                <span>General</span>
              </TabsTrigger>
              <TabsTrigger value="topics" className="flex items-center gap-2">
                <Book className="h-5 w-5" />
                <span>Topics</span>
              </TabsTrigger>
              <TabsTrigger value="mailing" className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                <span>Mailing</span>
              </TabsTrigger>
              <TabsTrigger
                value="subscriptions"
                className="flex items-center gap-2"
              >
                <Newspaper className="h-5 w-5" />
                <span>Subscriptions</span>
              </TabsTrigger>
            </TabsList>
            <TabsContent value="general">
              <General profile={editedProfile} setProfile={setEditedProfile} />
            </TabsContent>

            <TabsContent value="topics">
              <Topics profile={editedProfile} setProfile={setEditedProfile} />
            </TabsContent>

            <TabsContent value="mailing">
              <Mailing profile={editedProfile} setProfile={setEditedProfile} />
            </TabsContent>

            <TabsContent value="subscriptions">
              <Subscriptions
                profile={editedProfile}
                setProfile={setEditedProfile}
              />
            </TabsContent>
          </Tabs>
        </ScrollArea>
        <div className="flex justify-end">
          <Button
            type="button"
            disabled={isEqual(profile, editedProfile)}
            onClick={handleSave}
          >
            {isSaving ? "Saving..." : "Save changes"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
