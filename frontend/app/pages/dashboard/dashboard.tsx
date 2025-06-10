import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Newspaper, Plus, Rocket } from "lucide-react";
import { useSearchProfiles } from "~/hooks/api/search-profiles-api";
import { Button } from "~/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
} from "~/components/ui/breadcrumb";
import { useAuthorization } from "~/hooks/use-authorization";
import { useQuery } from "types/api";
import { useEffect } from "react";
import { toast } from "sonner";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import { sortBy } from "lodash-es";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";

const suppressSWRReloading = {
  refreshInterval: 0,
  refreshWhenHidden: false,
  revalidateOnFocus: false,
  refreshWhenOffline: false,
  revalidateIfStale: false,
  revalidateOnReconnect: false,
};

export function DashboardPage() {
  const { authorizationHeaders } = useAuthorization();

  // Todo: example
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { data, isLoading } = useQuery("/api/v1/search-profiles", {
    headers: authorizationHeaders,
  });
  const { data: profiles } = useSearchProfiles();

  return (
    <Layout>
      <Breadcrumb className="mt-8">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <Text hierachy={2}>Dashboard</Text>
      <Alert className="bg-blue-100 mb-3">
        <Rocket className="h-4 w-4" color="#113264" />
        <AlertTitle className="text-[#113264]">Heads up!</AlertTitle>
        <AlertDescription className="text-[#113264]">
          New press reviews available!
        </AlertDescription>
      </Alert>
      <Button className={"mb-4"}>
        <Newspaper /> Press Reviews
      </Button>
      <div className={"flex gap-5"}>
        <h2 className="text-2xl font-bold ">Profiles</h2>
        <Button variant="outline" className={"size-8"}>
          <Plus />
        </Button>
      </div>
      <div className="flex flex-wrap gap-6 mt-4 mb-4">
        {profiles?.map((profile) => (
          <ProfileCard
            key={profile.id}
            title={profile.name}
            newArticles={profile.newArticles}
            imageUrl={profile.imageUrl}
          />
        ))}
      </div>
      <h2 className="text-2xl font-bold mb-4">Trend Analysis</h2>
    </Layout>
  );
}
