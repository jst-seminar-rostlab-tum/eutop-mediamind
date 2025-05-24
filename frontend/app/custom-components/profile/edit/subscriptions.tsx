import type { Subscription } from "~/types/profile";
import { DataTable } from "~/custom-components/profile/edit/data-table";
import { Label } from "~/components/ui/label";

export interface SubscriptionsProps {
  subscriptions: Subscription[];
}

export function Subscriptions({ subscriptions }: SubscriptionsProps) {
  const subscriptionWebsites = subscriptions.map(
    (subscriptions) => subscriptions.name,
  );
  return (
    <div>
      <h2 className={"font-bold pt-3 pb-3"}>Sources</h2>
      <Label className={"text-gray-400 font-normal pb-4"}>
        Configure web scraping sources
      </Label>
      <DataTable name={"Source"} dataArray={subscriptionWebsites}></DataTable>
    </div>
  );
}
