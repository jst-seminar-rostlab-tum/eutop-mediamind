import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Loader2, Plus } from "lucide-react";
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
import { BreakingNews } from "./breaking-news";
import Layout from "~/custom-components/layout";
import "./dashboard.css";
import { useTranslation } from "react-i18next";
import { FilterBar } from "~/custom-components/dashboard/filter-bar";
import type { Profile } from "../../../types/model";

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
  } else if (profile.can_read_user_ids.includes(userId)) {
    return "reader";
  }
  return "";
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
  const {
    data: profiles,
    isLoading,
    error,
    mutate,
  } = useQuery("/api/v1/search-profiles", undefined, suppressSWRReloading);

  const {
    data: me,
    error: meError,
    isLoading: meLoading,
  } = useQuery("/api/v1/users/me");

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
      toast.error("Failed to load profiles.");
    }
    if (meError) {
      toast.error("Failed to load user information.");
    }
  }, [error, meError]);

  const breakingNews = [
    {
      title:
        "World Bank sharply cuts global growth outlook on trade turbulence",
      description:
        "This would mark the slowest rate of global growth since 2008, aside from outright global recessions. It now expects the global economy to expand by 2.3% in 2025, down from an earlier forecast of 2.7%",
    },
    {
      title: "Uber brings forward trialling driverless taxis in UK",
      description:
        "The ride-hailing app will work with the UK artificial intelligence (AI) firm Wayve, which has been testing out the technology on the city's streets with human oversight, in line with current legislation.",
    },
    {
      title: "US and China meet for trade talks in London",
      description:
        "A senior US delegation including Commerce Secretary Howard Lutnick met Chinese representatives such as Vice Premier He Lifeng at Lancaster House to resolve tension",
    },
    {
      title: "Europe heaps harsh sanctions on Russia",
      description:
        "he European Union announced a new package of sanctions against Russia on Tuesday",
    },
    {
      title: "Massive Russian drone attack slams Kyiv",
      description:
        "ussia launched 315 drones at Ukraine overnight into Tuesday, in what Ukrainian President Volodymyr Zelensky said was “one of the largest” attacks on the capital Kyiv so far.",
    },
    {
      title:
        "Greta Thunberg departs Israel on flight to Paris after detention aboard aid ship",
      description:
        "Swedish climate and human rights activist Greta Thunberg departed Israel on a flight to France on Tuesday after being detained by Israeli forces",
    },
  ];
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  return (
    <Layout>
      <Breadcrumb className="mt-8">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-bold mb-2 mt-1">
        {t("dashboard.dashboard")}
      </h1>
      <BreakingNews breakingNews={breakingNews} />
      <div className={"flex gap-5 mb-3"}>
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
      {isLoading || meLoading || !me ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2 text-muted-foreground">
            {t("dashboard.profiles_loading")}
          </span>
        </div>
      ) : (
        <div className="grid-profile-cards mt-4 mb-4">
          {filteredAndSortedProfiles?.map((profile, idx) => (
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
