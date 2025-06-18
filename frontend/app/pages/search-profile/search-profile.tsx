import { Book, Mail, Search } from "lucide-react";
import { /*useEffect,*/ useMemo, useState } from "react";
import { useParams } from "react-router";
import { useQuery } from "types/api";
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

import { SidebarFilter } from "./sidebar-filter";

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

  if (!id) return null;

  const {
    data: profile,
    //isLoading: isProfileLoading,
    //error: profileError,
    //mutate: mutateProfile,
  } = useQuery(
    "/api/v1/search-profiles/{search_profile_id}",
    { params: { path: { search_profile_id: id } } },
    suppressSWRReloading,
  );

  // add skeletton or no matches later when Endpoints work
  /*
    if (isLoading) return <Skeleton />;
    if (error) return <p>Error loading matches</p>;
    */

  const articles = [
    {
      title: "BMW builds new Mock Data Factory in Munich",
      summary:
        "BMW decided to build a new factory in Munich, the Mock Data will be produced there from now on. The project cost approximately 200 Mio Euros. The city of Munich is happy. The text will then break here because who reads more then two rows at first look anyways",
      topics: ["Automotive", "Envorionmental", "Factory"],
      relevance_score: "9.8",
      published_at: "2025-06-01T22:23:47.862Z",
      url: "BMW.de",
    },
    {
      title: "Mercedes is working on new Mock Articles",
      summary:
        "Mercedes will extend its Mock Article range to include more Data for this Page. WHY? IDK to be honest, I just need Mock data because the Bachend is not working. The text will then break here because two rows is enough",
      topics: ["Automotive", "Mock-Data"],
      relevance_score: "6.5",
      published_at: "2025-05-25T22:23:47.862Z",
      url: "Mercedes.de",
    },
    {
      title: "BMW is providing another Mock article for this Page",
      summary:
        "Since we need Data and the Endpoint is not working, BMW is doing more stuff to fill up this Article. They be doing this and that, and even more! They also added some mocked topics woohooo. The text will then break here because of more then 2 rows I guess",
      topics: ["Endpoints", "Backend", "Software"],
      relevance_score: "2.8",
      published_at: "2025-06-18T22:23:47.862Z",
      url: "BMW.de",
    },
    {
      title: "BMW is providing another Mock article for this Page",
      summary:
        "Since we need Data and the Endpoint is not working, BMW is doing more stuff to fill up this Article. They be doing this and that, and even more! They also added some mocked topics woohooo. The text will then break here because of more then 2 rows I guess",
      topics: ["Endpoints", "Backend", "Software"],
      relevance_score: "2.8",
      published_at: "2025-06-18T22:23:47.862Z",
      url: "BMW0.de",
    },
    {
      title: "BMW is providing another Mock article for this Page",
      summary:
        "Since we need Data and the Endpoint is not working, BMW is doing more stuff to fill up this Article. They be doing this and that, and even more! They also added some mocked topics woohooo. The text will then break here because of more then 2 rows I guess",
      topics: ["Endpoints", "Backend", "Software"],
      relevance_score: "2.8",
      published_at: "2025-06-18T22:23:47.862Z",
      url: "BMW1.de",
    },
    {
      title: "BMW is providing another Mock article for this Page",
      summary:
        "Since we need Data and the Endpoint is not working, BMW is doing more stuff to fill up this Article. They be doing this and that, and even more! They also added some mocked topics woohooo. The text will then break here because of more then 2 rows I guess",
      topics: ["Endpoints", "Backend", "Software"],
      relevance_score: "2.8",
      published_at: "2025-06-18T22:23:47.862Z",
      url: "BMW2.de",
    },
    {
      title: "BMW is providing another Mock article for this Page",
      summary:
        "Since we need Data and the Endpoint is not working, BMW is doing more stuff to fill up this Article. They be doing this and that, and even more! They also added some mocked topics woohooo. The text will then break here because of more then 2 rows I guess",
      topics: ["Endpoints", "Backend", "Software"],
      relevance_score: "2.8",
      published_at: "2025-06-18T22:23:47.862Z",
      url: "BMW3.de",
    },
  ];

  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"relevance" | "date">("relevance");

  const [searchSources, setSearchSources] = useState("");
  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const [searchTopics, setSearchTopics] = useState("");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);

  const [fromDate, setFromDate] = useState<Date | undefined>(undefined);

  const [toDate, setToDate] = useState<Date | undefined>(undefined);

  const filteredArticles = useMemo(() => {
    let filtered = articles.filter((a) =>
      a.title.toLowerCase().includes(search.toLowerCase()),
    );

    if (selectedSources.length > 0) {
      filtered = filtered.filter((a) => selectedSources.includes(a.url));
    }

    // every or some here?
    if (selectedTopics.length > 0) {
      filtered = filtered.filter((a) =>
        selectedTopics.every((topic) => a.topics.includes(topic)),
      );
    }

    if (fromDate) {
      filtered = filtered.filter((a) => new Date(a.published_at) >= fromDate);
    }

    // to end of day to catch most time zone shifts (ask in meeting about Zulu Time (UTC) conversion to German time by javascript)
    if (toDate) {
      const endOfDay = new Date(toDate);
      endOfDay.setHours(23, 59, 59, 999);
      filtered = filtered.filter((a) => new Date(a.published_at) <= endOfDay);
    }

    return filtered.sort((a, b) => {
      if (sortBy === "relevance") {
        return parseFloat(b.relevance_score) - parseFloat(a.relevance_score); // descending
      } else {
        return (
          new Date(b.published_at).getTime() -
          new Date(a.published_at).getTime()
        ); // descending
      }
    });
  }, [search, articles, sortBy]);

  // Extract unique sources from articles
  const uniqueSources = useMemo(() => {
    const urls = articles.map((a) => a.url);
    return Array.from(new Set(urls));
  }, [articles]);

  // Extract unique topics from articles
  const uniqueTopics = useMemo(() => {
    const allTopics = articles.flatMap((a) => a.topics); // flattens the nested arrays
    return Array.from(new Set(allTopics));
  }, [articles]);

  // maybe when unique sources available, check them all; causes infinit rerenders with mocked data, only needed when Endpoint ready
  /*
  useEffect(() => {
    setSelectedSources(uniqueSources);
  }, [uniqueSources]);
  */

  console.log(uniqueSources);

  return (
    <Layout>
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
      <Text hierachy={2}>{profile?.name}</Text>
      <div className="flex gap-3 items-center mt-2">
        <Book size={20} />
        <p>Topics:</p>
        {profile?.topics?.map((topic, idx) => (
          <div className="bg-secondary rounded-lg py-1 px-2" key={idx}>
            {topic.name}
          </div>
        ))}
      </div>
      <div className="flex gap-3 items-center mt-2">
        <Mail />
        <p>Press releases: Date missing!</p>
      </div>

      <div className="w-full grid grid-cols-6 mt-10 gap-8">
        <div className="col-span-2">
          <SidebarFilter
            sortBy={sortBy}
            setSortBy={setSortBy}
            selectedSources={selectedSources}
            setSelectedSources={setSelectedSources}
            searchSources={searchSources}
            setSearchSources={setSearchSources}
            uniqueSources={uniqueSources}
            selectedTopics={selectedTopics}
            setSelectedTopics={setSelectedTopics}
            searchTopics={searchTopics}
            setSearchTopics={setSearchTopics}
            uniqueTopics={uniqueTopics}
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

          {filteredArticles.map((article, idx) => {
            const relevance = parseFloat(article.relevance_score);

            const bgColor =
              relevance > 7
                ? "bg-green-200"
                : relevance < 3
                  ? "bg-red-200"
                  : "bg-yellow-200";

            return (
              <Card className="mb-4 p-5 gap-4 justify-start" key={idx}>
                <CardTitle>{article.title}</CardTitle>
                <p>{truncateAtWord(article.summary, 205)}</p>
                <div className="flex gap-3 items-center">
                  <div className={`rounded-lg py-1 px-2 ${bgColor}`}>
                    Relevance: {article.relevance_score}
                  </div>
                  {article.topics.map((topic, idx) => (
                    <div
                      className="bg-secondary rounded-lg py-1 px-2"
                      key={idx}
                    >
                      {topic}
                    </div>
                  ))}
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </Layout>
  );
}
