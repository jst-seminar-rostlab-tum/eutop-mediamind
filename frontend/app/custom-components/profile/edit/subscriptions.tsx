import { Label } from "~/components/ui/label";
import { DataTableSubscriptions } from "~/custom-components/profile/edit/data-table-subscriptions";
import type { Profile, Subscription } from "../../../../types/model";
import { useQuery } from "types/api";
import { useAuthorization } from "~/hooks/use-authorization";

export interface SubscriptionsProps {
  profile: Profile;
  setProfile: (profile: Profile) => void;
}

export function Subscriptions({ profile, setProfile }: SubscriptionsProps) {
  const { authorizationHeaders } = useAuthorization();
  const { data: availableSubscriptions } = useQuery("/api/v1/subscriptions", {
    headers: authorizationHeaders,
  });

  const setSubscriptions = (subscriptions: Subscription[]) =>
    setProfile({ ...profile, subscriptions: subscriptions });

  const profileSubscriptions = availableSubscriptions?.map((availableSub) => {
    return {
      ...availableSub,
      is_subscribed: profile.subscriptions.some(
        (sub) => sub.name === availableSub.name && sub.is_subscribed,
      ),
    };
  });

  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Sources</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        Configure web scraping sources used for the external mailing list.
      </Label>
      <DataTableSubscriptions
        name={"Source"}
        allSubscriptions={profileSubscriptions || []}
        setSubscriptions={setSubscriptions}
      ></DataTableSubscriptions>
    </div>
  );
}
