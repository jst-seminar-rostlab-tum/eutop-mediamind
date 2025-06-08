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
import { useAuthorization } from "~/hooks/use-authorization";
import { useQuery } from "types/api";
import { useEffect } from "react";
import { toast } from "sonner";
import { EditProfile } from "~/custom-components/profile/edit/edit-profile";

export function DashboardPage() {
  const { authorizationHeaders } = useAuthorization();

  const {
    data: profiles,
    isLoading,
    error,
  } = useQuery(
    "/api/v1/search-profiles",
    {
      headers: authorizationHeaders,
    },
    { refreshInterval: 0, refreshWhenHidden: false, revalidateOnFocus: false },
  );

  useEffect(() => {
    if (error) {
      console.error("Failed to load profiles:", error);
      toast.error("Failed to load profiles.");
    }
  }, [error]);

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
          <EditProfile
            mode="create"
            organizationId="3fa85f64-5717-4562-b3fc-2c963f66afa6" //TODO
            trigger={
              <Button variant="outline" className={"size-8"}>
                <Plus />
              </Button>
            }
          />
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
        <div className="flex flex-wrap gap-6 mt-4 mb-4">
          {profiles?.map((profile) => (
            <ProfileCard key={profile.id} profile={profile} />
          ))}
        </div>
      )}
      <h2 className="text-2xl font-bold mb-4">Trend Analysis</h2>
    </div>
  );
}
