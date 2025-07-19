import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Info, Plus } from "lucide-react";
import { Button } from "~/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
} from "~/components/ui/breadcrumb";
import { useQuery } from "types/api";
import { useEffect, useState, useMemo } from "react";
import { toast } from "sonner";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";
import { sortBy } from "lodash-es";
import Layout from "~/custom-components/layout";
import "./dashboard.css";
import { Alert, AlertTitle } from "~/components/ui/alert";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import { FilterBar } from "~/custom-components/dashboard/filter-bar";
import type { Profile } from "../../../types/model";
import { useAuthorization } from "~/hooks/use-authorization";
import { ProfileCardSkeleton } from "~/custom-components/dashboard/profile-card-skeleton";
import Text from "~/custom-components/text";

const suppressSWRReloading = {
  refreshInterval: 0,
  refreshWhenHidden: false,
  revalidateOnFocus: false,
  refreshWhenOffline: false,
  revalidateIfStale: false,
  revalidateOnReconnect: false,
};

interface FilterState {
  showUpdatedOnly: boolean;
  selectedRole: string;
  selectedVisibility: string;
}

function getUserRole(profile: Profile, userId: string): string {
  if (profile.owner_id === userId) {
    return "owner";
  } else if (profile.can_edit_user_ids.includes(userId)) {
    return "editor";
  }
  return "reader";
}

function getProfileVisibility(profile: Profile, userId: string): string {
  if (profile.is_public) {
    return "public";
  }

  const totalUsersWithAccess = new Set([
    ...profile.can_read_user_ids,
    ...profile.can_edit_user_ids,
  ]).size;

  if (
    totalUsersWithAccess === 0 ||
    (totalUsersWithAccess === 1 && profile.owner_id === userId)
  ) {
    return "private";
  }

  return "shared";
}

export function DashboardPage() {
  const { user: me } = useAuthorization();
  const {
    data: profiles,
    isLoading,
    error,
    mutate,
  } = useQuery("/api/v1/search-profiles", undefined, suppressSWRReloading);
  const { t } = useTranslation();

  const [filters, setFilters] = useState<FilterState>({
    showUpdatedOnly: false,
    selectedRole: "",
    selectedVisibility: "",
  });

  const filteredAndSortedProfiles = useMemo(() => {
    if (!profiles || !me) return [];

    const filtered = profiles.filter((profile: Profile) => {
      if (filters.showUpdatedOnly && profile.new_articles_count === 0) {
        return false;
      }

      if (filters.selectedRole) {
        const userRole = getUserRole(profile, me.id);
        if (userRole !== filters.selectedRole) {
          return false;
        }
      }

      if (filters.selectedVisibility) {
        const visibility = getProfileVisibility(profile, me.id);
        if (visibility !== filters.selectedVisibility) {
          return false;
        }
      }

      return true;
    });

    return sortBy(filtered, "name");
  }, [profiles, me, filters]);

  useEffect(() => {
    if (error) {
      toast.error(t("dashboard.loading_failed"));
    }
  }, [error]);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  return (
    <Layout>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/dashboard">{t("breadcrumb_home")}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <Text hierachy={2}>{t("dashboard.dashboard")}</Text>
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
      <FilterBar onFiltersChange={setFilters} />
      {!isLoading && filteredAndSortedProfiles?.length === 0 ? (
        <div className="flex items-center justify-center py-8">
          <span className="text-gray-400">
            {t("dashboard.no_matched_profiles")}
          </span>
        </div>
      ) : (
        <div className="grid-profile-cards mt-4 mb-4">
          {isLoading || !me
            ? Array.from({ length: 8 }).map((_, idx) => (
                <ProfileCardSkeleton key={idx} />
              ))
            : filteredAndSortedProfiles?.map((profile, idx) => (
                <ProfileCard
                  key={profile.id + idx}
                  profile={profile}
                  mutateDashboard={mutate}
                  profile_id={me.id}
                />
              ))}
        </div>
      )}
    </Layout>
  );
}
