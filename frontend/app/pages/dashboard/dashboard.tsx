import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Alert, AlertDescription, AlertTitle } from "~/components/ui/alert";
import { Loader2, Newspaper, Plus, Rocket } from "lucide-react";
import { Button } from "~/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
} from "~/components/ui/breadcrumb";
import { useQuery } from "types/api";
import { useEffect } from "react";
import { toast } from "sonner";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import { sortBy } from "lodash-es";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import "./dashboard.css";

const suppressSWRReloading = {
  refreshInterval: 0,
  refreshWhenHidden: false,
  revalidateOnFocus: false,
  refreshWhenOffline: false,
  revalidateIfStale: false,
  revalidateOnReconnect: false,
};

export function DashboardPage() {
  const {
    data: profiles,
    isLoading,
    error,
    mutate,
  } = useQuery("/api/v1/search-profiles", undefined, suppressSWRReloading);

  const sortedProfiles = sortBy(profiles, "name");

  useEffect(() => {
    if (error) {
      toast.error("Failed to load profiles.");
    }
  }, [error]);

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
        <EditProfile
          mutateDashboard={mutate}
          trigger={
            <Button variant="outline" className={"size-8"}>
              <Plus />
            </Button>
          }
        />
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2 text-muted-foreground">
            Loading profiles...
          </span>
        </div>
      ) : (
        <div className="grid-profile-cards mt-4 mb-4">
          {sortedProfiles?.map((profile) => (
            <ProfileCard
              key={profile.id}
              profile={profile}
              mutateDashboard={mutate}
            />
          ))}
        </div>
      )}
      <h2 className="text-2xl font-bold mb-4">Trend Analysis</h2>
    </Layout>
  );
}
