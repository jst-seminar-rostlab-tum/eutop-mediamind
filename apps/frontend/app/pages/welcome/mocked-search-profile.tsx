import { Book, FileText, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Card, CardTitle } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import Text from "~/custom-components/text";
import {
  getLocalizedContent,
  getPercentage,
  truncateAtWord,
} from "~/lib/utils";
import { MockedSidebarFilter } from "./mocked-sidebar-filter";
import { ScrollArea, ScrollBar } from "~/components/ui/scroll-area";
import { useTranslation } from "react-i18next";
import { Button } from "~/components/ui/button";
import { toast } from "sonner";

export function MockedSearchProfileOverview() {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"relevance" | "date">("relevance");

  const [searchSources, setSearchSources] = useState("");

  const [searchTopics, setSearchTopics] = useState("");

  const [fromDate, setFromDate] = useState<Date>();
  const [toDate, setToDate] = useState<Date>();
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>([]);

  const [searchTerm, setSearchTerm] = useState<string>("");

  const { t } = useTranslation();

  const profile = {
    id: "1",
    name: "Eutop",
    is_public: true,
    organization_emails: ["user@example.com"],
    profile_emails: ["user@example.com"],
    can_read_user_ids: ["1"],
    is_reader: true,
    can_edit_user_ids: ["1"],
    is_editor: true,
    owner_id: "1",
    is_owner: true,
    language: "en",
    topics: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "Automotive",
        keywords: ["Tires", "Engine"],
      },
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afb7",
        name: "Environment",
        keywords: ["CO2", "Renewable Energy"],
      },
    ],
    subscriptions: [
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afy4",
        name: "Spiegel",
        is_subscribed: true,
      },
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afx1",
        name: "Welt",
        is_subscribed: true,
      },
      {
        id: "3fa85f64-5717-4562-b3fc-2c963f66afz2",
        name: "FAZ",
        is_subscribed: true,
      },
    ],
    new_articles_count: 3,
  };

  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  const matches = [
    {
      id: "1",
      relevance: 0.9,
      topics: [
        {
          id: "1",
          name: "Automotive",
          score: 0.95,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Cars: A Reliable Way to Get from A to B",
          de: "Autos: Eine zuverlässige Art, von A nach B zu kommen",
        },
        summary: {
          en: "Cars have long been a trusted method of transportation.\nThey offer flexibility, speed, and convenience.\nWhile public transport is growing, cars remain essential.\nMost families rely on at least one vehicle.\nInfrastructure continues to favor personal vehicles.",
          de: "Autos sind seit langem ein bewährtes Fortbewegungsmittel.\nSie bieten Flexibilität, Geschwindigkeit und Komfort.\nObwohl der öffentliche Verkehr zunimmt, bleiben Autos wichtig.\nDie meisten Familien besitzen mindestens ein Auto.\nDie Infrastruktur bevorzugt weiterhin den Individualverkehr.",
        },
        image_urls: ["https://picsum.photos/800/600?random=10"],
        date: "2025-07-16",
      },
    },
    {
      id: "2",
      relevance: 0.88,
      topics: [
        {
          id: "2",
          name: "Environmental",
          score: 0.9,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Summer Temperatures Are on the Rise",
          de: "Die Sommertemperaturen steigen an",
        },
        summary: {
          en: "This summer has been one of the hottest on record.\nCities across the globe report increased heat waves.\nScientists link the rise to climate change.\nCitizens are encouraged to reduce energy use.\nGovernments are pushing for climate adaptation strategies.",
          de: "Dieser Sommer gehört zu den heißesten seit Beginn der Aufzeichnungen.\nStädte weltweit berichten von Hitzewellen.\nWissenschaftler sehen einen Zusammenhang mit dem Klimawandel.\nBürger sollen ihren Energieverbrauch senken.\nRegierungen fördern Anpassungsstrategien.",
        },
        image_urls: ["https://picsum.photos/800/600?random=9"],
        date: "2025-07-16",
      },
    },
    {
      id: "3",
      relevance: 0.85,
      topics: [
        {
          id: "3",
          name: "Automotive",
          score: 0.88,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Electric Cars Gaining Popularity in Europe",
          de: "Elektroautos werden in Europa immer beliebter",
        },
        summary: {
          en: "More people are switching to electric cars every year.\nGovernment incentives are helping to lower costs.\nCharging infrastructure is expanding rapidly.\nAutomakers are releasing new models frequently.\nPublic perception of EVs is becoming more positive.",
          de: "Immer mehr Menschen steigen auf Elektroautos um.\nStaatliche Förderungen senken die Kosten.\nDie Ladeinfrastruktur wächst schnell.\nAutohersteller bringen regelmäßig neue Modelle heraus.\nDas öffentliche Bild von E-Autos verbessert sich.",
        },
        image_urls: ["https://picsum.photos/800/600?random=8"],
        date: "2025-07-08",
      },
    },
    {
      id: "4",
      relevance: 0.86,
      topics: [
        {
          id: "4",
          name: "Environmental",
          score: 0.93,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Wind Energy Now Powers 20% of Local Grid",
          de: "Windenergie deckt nun 20 % des lokalen Stromnetzes",
        },
        summary: {
          en: "Wind turbines are generating a larger share of electricity.\nRural areas have seen major investment in renewables.\nMaintenance costs for wind farms are decreasing.\nLocal jobs are created through green energy projects.\nGrid upgrades improve renewable integration.",
          de: "Windkraft erzeugt einen immer größeren Teil des Stroms.\nLändliche Regionen profitieren von Investitionen.\nWartungskosten für Windparks sinken.\nGrüne Energie schafft neue Arbeitsplätze.\nNetzmodernisierungen erleichtern die Integration.",
        },
        image_urls: ["https://picsum.photos/800/600?random=7"],
        date: "2025-07-08",
      },
    },
    {
      id: "5",
      relevance: 0.8,
      topics: [
        {
          id: "5",
          name: "Automotive",
          score: 0.82,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Routine Oil Changes Extend Engine Life",
          de: "Regelmäßiger Ölwechsel verlängert die Lebensdauer des Motors",
        },
        summary: {
          en: "Experts recommend changing oil every 10,000 km.\nClean oil helps engines run smoothly.\nDelaying oil changes can cause damage.\nMost manufacturers include oil change schedules.\nNewer cars have reminders for maintenance.",
          de: "Experten empfehlen einen Ölwechsel alle 10.000 km.\nSauberes Öl sorgt für einen reibungslosen Motorlauf.\nVerspätete Ölwechsel können Schäden verursachen.\nHersteller geben Wartungsintervalle vor.\nModerne Autos erinnern an den nächsten Ölwechsel.",
        },
        image_urls: ["https://picsum.photos/800/600?random=6"],
        date: "2025-07-02",
      },
    },
    {
      id: "6",
      relevance: 0.84,
      topics: [
        {
          id: "6",
          name: "Environmental",
          score: 0.85,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Cities Invest in Urban Tree Planting",
          de: "Städte investieren in städtische Baumpflanzungen",
        },
        summary: {
          en: "Urban trees help cool cities and reduce pollution.\nMunicipalities are launching tree planting campaigns.\nTrees also improve mental well-being.\nGreen areas are linked to higher property values.\nCitizens are encouraged to volunteer for planting.",
          de: "Stadtbäume kühlen und verringern die Luftverschmutzung.\nKommunen starten Baumpflanzaktionen.\nBäume fördern auch das psychische Wohlbefinden.\nGrünflächen steigern Immobilienwerte.\nBürger sollen sich an Pflanzaktionen beteiligen.",
        },
        image_urls: ["https://picsum.photos/800/600?random=5"],
        date: "2025-06-16",
      },
    },
    {
      id: "7",
      relevance: 0.75,
      topics: [
        {
          id: "7",
          name: "Automotive",
          score: 0.78,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "The Future of Self-Driving Cars",
          de: "Die Zukunft selbstfahrender Autos",
        },
        summary: {
          en: "Self-driving technology is advancing quickly.\nMajor tech firms are investing heavily.\nSafety remains the top concern.\nLegal frameworks are under development.\nPilot programs are testing in urban areas.",
          de: "Selbstfahrende Technologie entwickelt sich schnell.\nGroße Technologiekonzerne investieren stark.\nSicherheit hat höchste Priorität.\nRechtliche Rahmenbedingungen entstehen.\nPilotprojekte testen in Städten.",
        },
        image_urls: ["https://picsum.photos/800/600?random=4"],
        date: "2025-06-10",
      },
    },
    {
      id: "8",
      relevance: 0.83,
      topics: [
        {
          id: "8",
          name: "Environmental",
          score: 0.88,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Plastic Waste Still a Global Problem",
          de: "Plastikmüll bleibt ein globales Problem",
        },
        summary: {
          en: "Plastic continues to pollute oceans and landfills.\nRecycling rates are improving but remain low.\nSingle-use bans are gaining traction.\nNew materials offer eco-friendly alternatives.\nConsumers are shifting to reusable items.",
          de: "Plastik verschmutzt weiter Meere und Deponien.\nRecyclingquoten steigen langsam.\nVerbote von Einwegplastik nehmen zu.\nNeue Materialien bieten umweltfreundliche Optionen.\nVerbraucher greifen öfter zu wiederverwendbaren Produkten.",
        },
        image_urls: ["https://picsum.photos/800/600?random=3"],
        date: "2025-05-24",
      },
    },
    {
      id: "9",
      relevance: 0.79,
      topics: [
        {
          id: "9",
          name: "Automotive",
          score: 0.76,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Tire Pressure Impacts Fuel Economy",
          de: "Reifendruck beeinflusst den Kraftstoffverbrauch",
        },
        summary: {
          en: "Proper tire pressure improves mileage.\nUnderinflated tires cause drag and waste fuel.\nDrivers should check pressure monthly.\nMost cars now include tire pressure sensors.\nMaintaining correct pressure extends tire life.",
          de: "Richtiger Reifendruck verbessert den Verbrauch.\nZu wenig Luft erhöht den Rollwiderstand.\nRegelmäßige Kontrolle wird empfohlen.\nModerne Autos haben Reifendrucksensoren.\nRichtiger Druck verlängert die Lebensdauer der Reifen.",
        },
        image_urls: ["https://picsum.photos/800/600?random=2"],
        date: "2025-07-15",
      },
    },
    {
      id: "10",
      relevance: 0.91,
      topics: [
        {
          id: "10",
          name: "Environmental",
          score: 0.96,
          keywords: [],
        },
      ],
      article: {
        article_url: "",
        headline: {
          en: "Renewable Energy Hits Record Output",
          de: "Erneuerbare Energien erreichen Rekordproduktion",
        },
        summary: {
          en: "Wind, solar, and hydro combined for a new record.\nFossil fuel use continues to decline globally.\nMore countries are adopting clean energy goals.\nInvestment in renewables is at an all-time high.\nExperts predict further growth in the coming years.",
          de: "Wind, Sonne und Wasser erzielen neue Rekorde.\nFossile Brennstoffe werden weniger genutzt.\nImmer mehr Länder setzen auf saubere Energie.\nInvestitionen in Erneuerbare erreichen Höchstwerte.\nExperten erwarten weiteres Wachstum.",
        },
        image_urls: ["https://picsum.photos/800/600?random=1"],
        date: "2025-06-28",
      },
    },
  ];

  useEffect(() => {}, [
    fromDate,
    toDate,
    sortBy,
    searchTerm,
    selectedTopics,
    selectedSources,
  ]);

  const Sources = profile ? profile.subscriptions : [];
  const Topics = profile ? profile.topics : [];

  return (
    <div className="w-full grow flex flex-col overflow-hidden">
      <div className="w-full flex flex-col justify-start">
        <div className="flex gap-6 items-center">
          <Text hierachy={2}>{profile?.name}</Text>
        </div>
        <div className="flex items-center justify-between mb-4 gap-10">
          <ScrollArea className="grow overflow-x-hidden whitespace-nowrap rounded-md pb-1.5">
            <div className="flex w-max space-x-2 p-1">
              <div className="flex items-center gap-1 shrink-0">
                <Book size={20} />
                <p className="font-bold">{t("search_profile.Topics")}</p>
              </div>
              {profile?.topics?.map((topic, idx) => (
                <div
                  className="bg-gray-200 rounded-lg py-1 px-2 shrink-0"
                  key={idx}
                >
                  {topic.name}
                </div>
              ))}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
          <Button asChild>
            <span
              className="inline-flex items-center gap-2"
              onClick={() => toast.info(t("landing_page.click_reports"))}
            >
              <FileText />
              {t("reports.reports")}
            </span>
          </Button>
        </div>
      </div>

      <div className="overflow-hidden grow flex flex-row justify-start mt-2 mb-4 gap-8">
        <div className="max-w-[400px] h-full">
          <MockedSidebarFilter
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
        <div className="min-w-[500px] grow flex flex-col overflow-hidden">
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
          <div className="bg-card rounded-lg border shadow-sm grow overflow-hidden">
            <div className="h-full">
              <ScrollArea className="p-4 h-full">
                {matches.map((match) => {
                  const relevance = match.relevance;

                  const bgColor =
                    relevance > 0.7
                      ? "bg-green-200"
                      : relevance < 0.3
                        ? "bg-red-200"
                        : "bg-yellow-200";

                  return (
                    <Card
                      className="mb-4 p-5 gap-4 justify-start"
                      key={match.id}
                    >
                      <div className="flex flex-row gap-4">
                        <img
                          src={match.article.image_urls[0]}
                          alt={getLocalizedContent(match.article.headline)}
                          className="w-[130px] h-[130px] object-cover rounded-md shadow-md shrink-0"
                        />
                        <div className="flex flex-col justify-evenly gap-4 p-2">
                          <CardTitle className="text-xl">
                            {getLocalizedContent(match.article.headline)}
                          </CardTitle>
                          <p>
                            {truncateAtWord(
                              getLocalizedContent(match.article.summary),
                              190,
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-3 items-center">
                        <div className={`rounded-lg py-1 px-2 ${bgColor}`}>
                          {t("search_profile.Relevance")}{" "}
                          {getPercentage(relevance)}
                        </div>
                        {match.topics.map((topic) => (
                          <div
                            className="bg-gray-200 rounded-lg py-1 px-2"
                            key={topic.id}
                          >
                            {getPercentage(topic.score) + " " + topic.name}
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
      </div>
    </div>
  );
}
