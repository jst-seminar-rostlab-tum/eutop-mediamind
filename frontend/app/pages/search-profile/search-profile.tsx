import { Book, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router";
import { client, useQuery } from "types/api";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "~/components/ui/breadcrumb";
import { Card, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import { truncateAtWord } from "~/lib/utils";
import { useNavigate } from "react-router";
import { SidebarFilter } from "./sidebar-filter";
import { ScrollArea } from "~/components/ui/scroll-area";
import type { paths } from "types/api-types-v1";
import { SearchProfileSkeleton } from "./search-profile-skeleton";

const suppressSWRReloading = {
  refreshInterval: 0,
  refreshWhenHidden: false,
  revalidateOnFocus: false,
  refreshWhenOffline: false,
  revalidateIfStale: false,
  revalidateOnReconnect: false,
};

export function SearchProfileOverview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"relevance" | "date">("relevance");

  const [searchSources, setSearchSources] = useState("");

  const [searchTopics, setSearchTopics] = useState("");

  const [fromDate, setFromDate] = useState<Date>();
  const [toDate, setToDate] = useState<Date>();
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [profileReady, setProfileReady] = useState<boolean>(false);

  type MatchesResponse =
    paths["/api/v1/search-profiles/{search_profile_id}/matches"]["post"]["responses"]["200"]["content"]["application/json"];

  const [matches, setMatches] = useState<MatchesResponse | undefined>(
    undefined,
  );

  useEffect(() => {
    if (!id) {
      navigate("/error/404");
    }
  }, [id, navigate]);

  const {
    data: profile,
    isLoading: isProfileLoading,
    error: profileError,
    //mutate: mutateProfile,
  } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}",
    { params: { path: { search_profile_id: id! } } },
    suppressSWRReloading,
  );

  useEffect(() => {
    if (profileError) {
      navigate("/error/404");
    }
  }, [profileError, navigate]);

  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  useEffect(() => {
    //init base matches search for first POST
    if (!profileError && profile && profile.subscriptions && profile.topics) {
      const subscriptionIds = profile.subscriptions.map((s) => s.id);
      const topicsIds = profile.topics.map((s) => s.id);
      setSelectedSources(subscriptionIds);
      setSelectedTopics(topicsIds);

      setFromDate(yesterday);
      setToDate(today);

      setProfileReady(true);
    }
  }, [profile, profileError]);

  useEffect(() => {
    if (!profileReady) return;

    const requestBody = {
      startDate: fromDate
        ? fromDate.toISOString().split("T")[0]
        : yesterday.toISOString().split("T")[0],
      endDate: toDate
        ? toDate.toISOString().split("T")[0]
        : today.toISOString().split("T")[0],
      sorting: sortBy.toUpperCase() as "DATE" | "RELEVANCE",
      searchTerm: "",
      topics: selectedTopics,
      subscriptions: selectedSources,
    };
    client
      .POST("/api/v1/search-profiles/{search_profile_id}/matches", {
        params: {
          path: { search_profile_id: id! },
        },
        body: requestBody,
      })
      .then(({ data, error }) => {
        if (data) {
          setMatches(data);
        } else if (error) {
          console.error("Error fetching matches:", error);
        }
      });
  }, [id, fromDate, toDate, sortBy, search, selectedTopics, selectedSources]);

  const filteredMatches = useMemo(() => {
    if (!matches) return [];

    return matches?.matches.filter((match) =>
      match.article.headline["en"].toLowerCase().includes(search.toLowerCase()),
    );
  }, [search, matches]);

  const Sources = profile ? profile.subscriptions : [];
  const Topics = profile ? profile.topics : [];

  return (
    <Layout>
      {!profile || isProfileLoading ? (
        <SearchProfileSkeleton />
      ) : (
        <>
          <Breadcrumb className="mt-8">
            <BreadcrumbList>
              <BreadcrumbItem>
                <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                <BreadcrumbPage>{profile?.name}</BreadcrumbPage>
              </BreadcrumbItem>
            </BreadcrumbList>
          </Breadcrumb>
          <div className="flex gap-8">
            <Text hierachy={2}>{profile?.name}</Text>
            <div className="flex gap-3 items-center">
              <Book size={20} />
              <p>Topics:</p>
              {profile?.topics?.map((topic, idx) => (
                <div className="bg-secondary rounded-lg py-1 px-2" key={idx}>
                  {topic.name}
                </div>
              ))}
            </div>
          </div>

          <div className="w-full grid grid-cols-6 mt-2 gap-8">
            <div className="col-span-2">
              <SidebarFilter
                sortBy={sortBy}
                setSortBy={setSortBy}
                selectedSources={selectedSources}
                setSelectedSources={setSelectedSources}
                searchSources={searchSources}
                setSearchSources={setSearchSources}
                Sources={Sources}
                selectedTopics={selectedTopics}
                setSelectedTopics={setSelectedTopics}
                searchTopics={searchTopics}
                setSearchTopics={setSearchTopics}
                Topics={Topics}
                fromDate={fromDate}
                setFromDate={setFromDate}
                toDate={toDate}
                setToDate={setToDate}
              />
            </div>
            <div className="col-span-4">
              <div className="relative mb-4 w-full flex">
                <Input
                  placeholder="Search articles"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                <Search
                  size={20}
                  className="absolute right-3 top-2 text-muted-foreground"
                />
              </div>
              <div className="bg-card rounded-xl border shadow-sm">
                <ScrollArea className="h-[755px] p-4">
                  {filteredMatches?.map((match) => {
                    const relevance = match.relevance;

                    const bgColor =
                      relevance > 7
                        ? "bg-green-200"
                        : relevance < 3
                          ? "bg-red-200"
                          : "bg-yellow-200";

                    return (
                      <Card
                        className="mb-4 p-5 gap-4 justify-start"
                        key={match.id}
                      >
                        <CardTitle className="text-xl">
                          {match.article.headline["en"]}
                        </CardTitle>
                        <p>
                          {truncateAtWord(match.article.summary["en"], 190)}
                        </p>
                        <div className="flex gap-3 items-center">
                          <div className={`rounded-lg py-1 px-2 ${bgColor}`}>
                            Relevance: {relevance}
                          </div>
                          {match.topic.map((topic) => (
                            <div
                              className="bg-secondary rounded-lg py-1 px-2"
                              key={topic.id}
                            >
                              {topic.score + " " + topic.name}
                            </div>
                          ))}
                        </div>
                      </Card>
                    );
                  })}
                </ScrollArea>
              </div>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
