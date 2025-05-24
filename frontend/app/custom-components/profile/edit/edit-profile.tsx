import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "~/components/ui/dialog";
import { Button } from "~/components/ui/button";
import type { Profile } from "~/types/profile";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { Book, Mail, Newspaper } from "lucide-react";
import { KeywordField } from "~/custom-components/profile/edit/keyword-field";
import { useState } from "react";
import { Switch } from "~/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { Topics } from "~/custom-components/profile/edit/topics";
import { Mailing } from "~/custom-components/profile/edit/mailing";
import { Subscriptions } from "~/custom-components/profile/edit/subscriptions";
import useProfileSubscriptionsApi from "~/hooks/api/profile-subscriptions-api";
import { ScrollArea } from "~/components/ui/scroll-area";

interface EditProfileProps {
  profile: Profile;
}

export function EditProfile({ profile }: EditProfileProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Edit Profile</Button>
      </DialogTrigger>

      <DialogContent className={"min-w-1/2 rounded-3xl max-h-3/4"}>
        <DialogHeader>
          <div className={"flex items-center gap-5"}>
            <DialogTitle className={"text-xl"}>
              Edit Profile: {profile.name}
            </DialogTitle>
            <Switch />
          </div>
        </DialogHeader>

        <ScrollArea className="max-h-[60vh] pr-2">
          <Tabs defaultValue="topics" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
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

            <TabsContent value="topics">
              <Topics profile={profile} />
            </TabsContent>

            <TabsContent value="mailing">
              <Mailing profile={profile} />
            </TabsContent>

            <TabsContent value="subscriptions">
              <Subscriptions subscriptions={useProfileSubscriptionsApi()} />
            </TabsContent>
          </Tabs>
        </ScrollArea>
        <DialogFooter>
          <Button type="submit">Save changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
