import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Loader2, Megaphone, Plus } from "lucide-react";
import { Button } from "~/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
} from "~/components/ui/breadcrumb";
import { useQuery } from "types/api";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import { sortBy } from "lodash-es";
import Layout from "~/custom-components/layout";
import "./dashboard.css";
import { Alert, AlertTitle } from "~/components/ui/alert";
import { useNavigate } from "react-router";

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

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <Layout>
      <Breadcrumb className="mt-8">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <Alert
        onClick={() => navigate("/dashboard/breaking")}
        className="hover:bg-gray-100 hover:cursor-pointer mb-2"
      >
        <Megaphone />
        <AlertTitle>Click here to view the latest breaking news!</AlertTitle>
      </Alert>
      <div className={"flex gap-5"}>
        <h2 className="text-2xl font-bold ">Profiles</h2>
        <EditProfile
          mutateDashboard={mutate}
          dialogOpen={createDialogOpen}
          setDialogOpen={setCreateDialogOpen}
        />
        <Button
          variant="outline"
          className={"size-8"}
          onClick={() => setCreateDialogOpen(true)}
        >
          <Plus />
        </Button>
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
          {sortedProfiles?.map((profile, idx) => (
            <ProfileCard
              key={profile.id + idx}
              profile={profile}
              mutateDashboard={mutate}
            />
          ))}
        </div>
      )}
    </Layout>
  );
}
