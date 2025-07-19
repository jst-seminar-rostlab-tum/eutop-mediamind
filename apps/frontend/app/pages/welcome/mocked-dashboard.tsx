import { Info, Plus } from "lucide-react";
import { Button } from "~/components/ui/button";
import { useState, useMemo } from "react";
import { sortBy } from "lodash-es";
import { Alert, AlertTitle } from "~/components/ui/alert";
import { useTranslation } from "react-i18next";
import { FilterBar } from "~/custom-components/dashboard/filter-bar";
import type { Profile } from "../../../types/model";
import Text from "~/custom-components/text";
import { toast } from "sonner";
import { MockedProfileCard } from "./mocked-profile-card";
import { profiles } from "./mock-data";

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

export function MockedDashboardPage() {
  const me = {
    id: "1",
    clerk_id: "clerk123",
    email: "user@example.com",
    first_name: "Max",
    last_name: "mustermann",
    is_superuser: true,
    language: "en",
    gender: "male",
    role: "member",
    organization_id: "123",
    organization_name: "testOrg",
  };

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

  return (
    <div className="p-6 py-3">
      <Text className="pt-0" hierachy={2}>
        {t("dashboard.dashboard")}
      </Text>
      <Alert
        className="hover:bg-blue-100 mb-4 bg-blue-200 text-blue-900"
        onClick={() => toast.info(t("landing_page.breaking_toast"))}
      >
        <Info />
        <AlertTitle>{t("breaking-news.entry")}</AlertTitle>
      </Alert>
      <div className={"flex gap-5"}>
        <h2 className="text-2xl font-bold ">{t("dashboard.profile")}</h2>
        <Button
          variant="outline"
          className={"size-8"}
          onClick={() => toast.info(t("landing_page.sp_toast"))}
        >
          <Plus />
        </Button>
      </div>
      <FilterBar onFiltersChange={setFilters} />
      {filteredAndSortedProfiles?.length === 0 ? (
        <div className="flex items-center justify-center py-8">
          <span className="text-gray-400">
            {t("dashboard.no_matched_profiles")}
          </span>
        </div>
      ) : (
        <div className="mt-6 mb-4 flex flex-wrap gap-10 gap-y-8 mx-4">
          {filteredAndSortedProfiles?.map((profile, idx) => (
            <MockedProfileCard key={idx} profile={profile} profile_id={me.id} />
          ))}
        </div>
      )}
    </div>
  );
}
