import { Rocket, Settings } from "lucide-react";
import type { KeyedMutator } from "swr";

import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import type { Profile } from "../../../types/model";

interface ProfileCardProps {
  profile: Profile;
  mutateDashboard: KeyedMutator<Profile[]>;
}

export function ProfileCard({ profile, mutateDashboard }: ProfileCardProps) {
  return (
    <Card className="w-[260px] h-[230px] rounded-3xl shadow-[2px_2px_15px_rgba(0,0,0,0.1)] hover:shadow-none transition-shadow duration-300 ease-in-out">
      <CardHeader className="-mt-2">
        <div className={"flex justify-between"}>
          <div>
            <CardTitle className="font-semibold text-xl">
              {profile.name}
            </CardTitle>
          </div>
          <EditProfile
            profile={profile}
            mutateDashboard={mutateDashboard}
            trigger={
              <Button
                variant="outline"
                size="icon"
                className={"rounded-[13px]"}
              >
                <Settings />
              </Button>
            }
          />
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
  );
}
