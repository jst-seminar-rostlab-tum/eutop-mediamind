import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Info, Loader2, Plus } from "lucide-react";
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
import { Link } from "react-router";
import { useTranslation } from "react-i18next";

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

  const { t } = useTranslation();

  const sortedProfiles = sortBy(profiles, "name");

  useEffect(() => {
    if (error) {
      toast.error("Failed to load profiles.");
    }
  }, [error]);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  return (
    <Layout>
      <Breadcrumb className="mt-8">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">
              {t("breadcrumb_home")}
            </BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-bold mb-4">{t("dashboard.dashboard")}</h1>
      <Link to="/dashboard/breaking">
        <Alert className="hover:bg-blue-100 mb-4 bg-blue-200 text-blue-900">
          <Info />
          <AlertTitle>{t("breaking-news.entry")}</AlertTitle>
        </Alert>
      </Link>
      <div className={"flex gap-5"}>
        <h2 className="text-2xl font-bold ">{t("dashboard.profile")}</h2>
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
            {t("dashboard.profiles_loading")}
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
