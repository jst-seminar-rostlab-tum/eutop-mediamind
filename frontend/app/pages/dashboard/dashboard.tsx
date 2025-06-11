import { ProfileCard } from "~/custom-components/dashboard/profile-card";
import { Loader2, Plus } from "lucide-react";
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
import { BreakingNews } from "./breaking-news";

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

  const {
    data: profiles,
    isLoading,
    error,
    mutate,
  } = useQuery(
    "/api/v1/search-profiles",
    {
      headers: authorizationHeaders,
    },
    suppressSWRReloading,
  );

  const sortedProfiles = sortBy(profiles, "name");

  useEffect(() => {
    if (error) {
      toast.error("Failed to load profiles.");
    }
  }, [error]);

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

  return (
    <div className={" mx-auto w-full max-w-2xl xl:max-w-7xl mt-12"}>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/dashboard">Home</BreadcrumbLink>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <BreakingNews breakingNews={breakingNews} />
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
        <div className="flex flex-wrap gap-6 mt-4 mb-4">
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
    </div>
  );
}
