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
import { Book, Mail } from "lucide-react";
import { KeywordField } from "~/custom-components/profile/edit/keyword-field";
import { useState } from "react";
import { Switch } from "~/components/ui/switch";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "~/components/ui/accordion";
import { Topics } from "~/custom-components/profile/edit/topics";
import { Mailing } from "~/custom-components/profile/edit/mailing";

interface EditProfileProps {
  profile: Profile;
}

export function EditProfile({ profile }: EditProfileProps) {


  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Edit Profile</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[825px] rounded-3xl">
        <DialogHeader>
          <div className={"flex items-center gap-5"}>
            <DialogTitle className={"text-xl"}>Edit Profile: {profile.name}</DialogTitle>
            <Switch/>
          </div>
        </DialogHeader>

        <Accordion type="multiple" defaultValue={["topics", "mailing"]} className="w-full">
          <AccordionItem value="topics">
            <AccordionTrigger defaultChecked={true}>
              <div className={"flex items-center gap-2"}>
                <Book className="h-5 w-5" />
                <h2 className={"font-bold"}>Topics</h2>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <Topics profile={profile} />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="mailing">
            <AccordionTrigger >
              <div className={"flex items-center gap-4"}>
                <div className={"flex gap-2 items-center "}>
                  <Mail className="h-5 w-5" />
                  <h2 className={"font-bold"}>Mailing</h2>
                </div>
                <Switch defaultChecked={true} onClick={(e) => e.stopPropagation()} />
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <Mailing profile={profile}/>
            </AccordionContent>
          </AccordionItem>
        </Accordion>


      </DialogContent>
    </Dialog>
  );
}
