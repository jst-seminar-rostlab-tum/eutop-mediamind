import { Book, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
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
import { SearchProfileSkeleton } from "./search-profile-skeleton";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import type { MatchesResponse } from "types/model";

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

  const [searchTerm, setSearchTerm] = useState<string>("");

  const { t } = useTranslation();

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
      searchTerm: searchTerm,
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
  }, [
    id,
    fromDate,
    toDate,
    sortBy,
    searchTerm,
    selectedTopics,
    selectedSources,
  ]);

  console.log("Matches: ", matches);

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
                <BreadcrumbLink href="/dashboard">
                  {t("breadcrumbs.Dashboard")}
                </BreadcrumbLink>
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
              <p>{t("search_profile.Topics")}</p>
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
                  placeholder={t("Search") + " " + t("search_profile.articles")}
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                <Button
                  variant="default"
                  className="rounded-m ml-2"
                  onClick={() => setSearchTerm(search)}
                >
                  <Search />
                </Button>
              </div>
              <div className="bg-card rounded-xl border shadow-sm">
                <ScrollArea className="h-[755px] p-4">
                  {matches?.matches.length === 0 ? (
                    <p className="text-muted-foreground text-sm text-center pt-2 italic">
                      No matches found.
                    </p>
                  ) : (
                    matches?.matches.map((match) => {
                      const relevance = match.relevance;

                      const bgColor =
                        relevance > 7
                          ? "bg-green-200"
                          : relevance < 3
                            ? "bg-red-200"
                            : "bg-yellow-200";

                      return (
                        <Link to={`./${match.id}`}>
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
                              <div
                                className={`rounded-lg py-1 px-2 ${bgColor}`}
                              >
                                Relevance: {relevance}
                              </div>
                              {match.topics.map((topic) => (
                                <div
                                  className="bg-secondary rounded-lg py-1 px-2"
                                  key={topic.id}
                                >
                                  {topic.score + " " + topic.name}
                                </div>
                              ))}
                            </div>
                          </Card>
                        </Link>
                      );
                    })
                  )}
                </ScrollArea>
              </div>
            </div>
          </div>
        </>
      )}
    </Layout>
  );
}
