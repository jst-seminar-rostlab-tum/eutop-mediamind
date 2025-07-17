import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import Text from "~/custom-components/text";
import { useAuthorization } from "~/hooks/use-authorization";
import { useTranslation } from "react-i18next";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "~/components/ui/button";
import { ChevronLeft, ChevronRight, SquareArrowOutUpRight } from "lucide-react";
import { Card } from "~/components/ui/card";
import { MockedDashboardPage } from "./mocked-dashboard";
import { MockedTopics } from "./mocked-topics";
import { MockedSearchProfileOverview } from "./mocked-search-profile";
import { MockedArticlePage } from "./mocked-article";

export function Welcome() {
  const { isSignedIn, user } = useAuthorization();
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    if (isSignedIn && user?.organization_id) {
      navigate("/dashboard");
    }
  }, [isSignedIn, user?.organization_id, navigate]);

  const lines = [
    {
      text: t("landing_page.header_slogan"),
      className: "text-4xl md:text-5xl font-medium leading-tight mb-2",
      delay: 0,
    },
    {
      text: "Media Mind",
      className: "text-5xl md:text-6xl font-bold leading-tight mb-2",
      delay: 0.3,
    },
    {
      text: t("landing_page.header_description"),
      className: "text-3xl md:text-4xl font-medium",
      delay: 0.6,
    },
  ];

  // mocked profile
  const exampleProfile = {
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
        id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        name: "string",
        is_subscribed: true,
      },
    ],
    new_articles_count: 3,
  };

  // mocked full article
  const exampleArticle = {
    match_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    topics: [
      {
        id: "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        name: "Climate Change",
        score: 0.92,
        keywords: [
          "global warming",
          "carbon emissions",
          "renewable energy",
          "sustainability",
        ],
      },
      {
        id: "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        name: "Technology Innovation",
        score: 0.78,
        keywords: [
          "artificial intelligence",
          "machine learning",
          "automation",
          "digital transformation",
        ],
      },
      {
        id: "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
        name: "Economic Policy",
        score: 0.65,
        keywords: [
          "inflation",
          "monetary policy",
          "fiscal measures",
          "economic growth",
        ],
      },
    ],
    search_profile: {
      id: "123e4567-e89b-12d3-a456-426614174000",
      name: "Environmental Tech Reporter",
    },
    article: {
      article_url: "",
      headline: {
        en: "Revolutionary Solar Panel Technology Achieves 40% Efficiency Breakthrough",
        de: "Revolutionäre Solarpanel-Technologie erreicht 40% Effizienz-Durchbruch",
      },
      summary: {
        en: "Scientists at MIT have developed a new type of solar panel that achieves unprecedented 40% efficiency, potentially revolutionizing renewable energy adoption worldwide.",
        de: "Wissenschaftler am MIT haben einen neuen Typ von Solarpanel entwickelt, der eine beispiellose Effizienz von 40% erreicht und die weltweite Einführung erneuerbarer Energien revolutionieren könnte.",
      },
      text: {
        en: "In a groundbreaking development that could reshape the renewable energy landscape, researchers at the Massachusetts Institute of Technology have successfully created solar panels with an efficiency rate of 40%, marking a significant leap from current commercial panels that typically achieve 20-22% efficiency. The breakthrough involves a novel multi-junction cell design that captures a broader spectrum of sunlight, including infrared radiation that traditional panels cannot utilize. Dr. Sarah Chen, lead researcher on the project, explained that the new technology uses a combination of perovskite and silicon materials in a tandem configuration to optimize energy conversion. This innovation has the potential to drastically reduce the cost per watt of solar energy, making renewable sources more competitive with fossil fuels. In lab tests, the new panels maintained performance under varied lighting conditions and showed improved durability compared to standard photovoltaic cells. The team is now working on scaling the manufacturing process and partnering with industry leaders to bring the technology to market within the next few years. Experts in the field have hailed this as a major step forward in sustainable energy, with the potential to accelerate global decarbonization efforts and increase energy access in underserved regions.",
        de: "In einer bahnbrechenden Entwicklung, die die Landschaft der erneuerbaren Energien grundlegend verändern könnte, haben Forscher am Massachusetts Institute of Technology erfolgreich Solarpanels mit einer Effizienzrate von 40 % entwickelt, was einen bedeutenden Fortschritt gegenüber aktuellen kommerziellen Panels darstellt, die typischerweise nur 20–22 % Effizienz erreichen. Der Durchbruch beruht auf einem neuartigen Multi-Junction-Zellendesign, das ein breiteres Spektrum des Sonnenlichts einfängt, einschließlich Infrarotstrahlung, die von herkömmlichen Panels nicht genutzt werden kann. Dr. Sarah Chen, leitende Wissenschaftlerin des Projekts, erklärte, dass die neue Technologie eine Kombination aus Perowskit- und Silizium-Materialien in einer Tandemkonfiguration verwendet, um die Energieumwandlung zu maximieren. Diese Innovation könnte die Kosten pro Watt für Solarenergie erheblich senken und erneuerbare Energien noch wettbewerbsfähiger gegenüber fossilen Brennstoffen machen. In Labortests zeigten die neuen Panels eine stabile Leistung unter wechselnden Lichtbedingungen und eine verbesserte Haltbarkeit im Vergleich zu herkömmlichen Photovoltaikzellen. Das Team arbeitet nun daran, den Herstellungsprozess zu skalieren und mit Industriepartnern zusammenzuarbeiten, um die Technologie in den nächsten Jahren auf den Markt zu bringen. Experten bezeichnen diese Entwicklung als einen entscheidenden Fortschritt für nachhaltige Energie und eine wichtige Chance, den globalen CO2-Ausstoß zu verringern und den Zugang zu Energie weltweit zu verbessern.",
      },
      image_urls: [
        "https://picsum.photos/800/600?random=1",
        "https://picsum.photos/800/600?random=2",
        "https://picsum.photos/800/600?random=3",
        "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&h=600",
        "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800&h=600",
      ],
      published: "2024-07-14T10:30:00Z",
      crawled: "2024-07-14T10:45:00Z",
      newspaper_id: "mit-tech-review",
      authors: ["Dr. Sarah Chen", "Michael Rodriguez", "Jennifer Park"],
      categories: ["Technology", "Environment", "Science", "Energy"],
      status: "summarized" as const,
      language: "en",
    },
    entities: {
      organizations: ["MIT", "Massachusetts Institute of Technology"],
      people: ["Dr. Sarah Chen"],
      locations: ["Massachusetts", "United States"],
      technologies: [
        "solar panels",
        "perovskite",
        "silicon",
        "multi-junction cells",
      ],
    },
  };

  const [profile, setProfile] = useState(exampleProfile);

  const features = [
    {
      header: t("landing_page.topics_header"),
      text: t("landing_page.topics_text"),
      card: <MockedTopics profile={profile} setProfile={setProfile} />,
      key: "topics",
      zoom: 1.15,
      height: "h-110",
    },
    {
      header: t("landing_page.dashboard_header"),
      text: t("landing_page.dashboard_text"),
      card: <MockedDashboardPage />,
      key: "dashboard",
      zoom: 0.9,
      height: "h-195",
      width: "w-180",
    },
    {
      header: t("landing_page.search_profile_header"),
      text: t("landing_page.search_profile_text"),
      card: <MockedSearchProfileOverview />,
      key: "search-profile",
      zoom: 0.7,
      height: "h-245",
    },
    {
      header: t("landing_page.article_header"),
      text: t("landing_page.article_text"),
      card: (
        <MockedArticlePage
          searchProfileId={exampleArticle.search_profile.id}
          searchProfileName={exampleArticle.search_profile.name}
          article={exampleArticle}
          matchId={exampleArticle.match_id}
        />
      ),
      key: "article",
      zoom: 0.7,
      height: "h-245",
    },
  ];

  const [currentIndex, setCurrentIndex] = useState(0);
  const total = features.length;
  const [hasUserInteracted, setHasUserInteracted] = useState(false);
  const [direction, setDirection] = useState(1);

  useEffect(() => {
    if (hasUserInteracted) return; // prevents creating the interval

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % total);
    }, 15000);

    return () => clearInterval(interval); // cleanup when effect re-runs
  }, [total, hasUserInteracted]);

  useEffect(() => {
    if (!hasUserInteracted) return;

    const timeout = setTimeout(() => {
      setHasUserInteracted(false); // If user has interacted: Resume autoplay after 30 sec
    }, 30000);

    return () => clearTimeout(timeout);
  }, [hasUserInteracted]);

  return (
    <div className="overflow-auto">
      <div
        className="relative h-[50vh] w-full bg-cover bg-center"
        style={{
          backgroundImage: "url('/press_wallpaper.jpg')",
        }}
      >
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 to-transparent z-0" />

        {/* Text Content */}
        <div className="relative z-10 h-full flex flex-col justify-end p-16 pl-20 max-w-[830px] text-white">
          {lines.map((line, i) => (
            <motion.p
              key={i}
              className={line.className}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                delay: line.delay,
                duration: 0.6,
                ease: [0.25, 0.1, 0.25, 1],
              }}
            >
              {line.text}
            </motion.p>
          ))}
        </div>
      </div>
      {/* Features Section */}
      <div className="relative w-full flex justify-center items-center min-h-[1000px] overflow-hidden">
        {/* Features Section */}
        <div className="relative w-full overflow-hidden min-h-[1000px]">
          {/* Background stays fixed and behind */}
          <div className="absolute inset-0 bg-[linear-gradient(160deg,_#8a99a8_0%,_#e3ecf4_20%,_#f8fcfe_50%,_#e5e8eb_100%)] z-0" />

          {/* Animation container */}
          <div className="relative z-10 w-full h-[1000px]">
            <AnimatePresence mode="wait" initial={false} custom={direction}>
              <motion.div
                key={features[currentIndex].key}
                custom={direction}
                initial={{ x: direction > 0 ? 300 : -300, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: direction > 0 ? -300 : 300, opacity: 0 }}
                transition={{
                  x: {
                    duration: 0.5, // slide-in
                    ease: "easeInOut",
                  },
                  opacity: {
                    duration: 0.4, // fade-in
                    delay: 0,
                  },
                }}
                className="absolute top-0 left-0 w-full h-full flex justify-center items-center"
              >
                <div className="flex flex-row flex-wrap min-w-[1400px] justify-center items-center mx-30 gap-20">
                  <div className="flex flex-col max-w-[500px] gap-4">
                    <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
                      {features[currentIndex].header}
                    </p>
                    <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
                      {features[currentIndex].text}
                    </p>
                  </div>
                  <Card
                    style={{ zoom: features[currentIndex].zoom }}
                    className={`max-w-270 ${features[currentIndex].width ?? ""} ${features[currentIndex].height} border-8 p-6 py-3 overflow-hidden`}
                    onClick={() => {
                      setHasUserInteracted(true);
                    }}
                  >
                    {features[currentIndex].card}
                  </Card>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Navigation Arrows */}
          <div className="absolute top-1/2 left-16 transform -translate-y-1/2 z-20">
            <button
              onClick={() => {
                setDirection(-1);
                setHasUserInteracted(true);
                requestAnimationFrame(() => {
                  setCurrentIndex((prev) => (prev - 1 + total) % total);
                });
              }}
            >
              <ChevronLeft size={40} />
            </button>
          </div>
          <div className="absolute top-1/2 right-16 transform -translate-y-1/2 z-20">
            <button
              onClick={() => {
                setDirection(1);
                setHasUserInteracted(true);
                requestAnimationFrame(() => {
                  setCurrentIndex((prev) => (prev + 1) % total);
                });
              }}
            >
              <ChevronRight size={40} />
            </button>
          </div>

          {/* Stepper */}
          <div className="absolute bottom-18 left-0 right-0 flex justify-center gap-5 z-20">
            {features.map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentIndex(index);
                  setHasUserInteracted(true);
                }}
                className={`h-3 w-3 rounded-full transition-all duration-300 ${
                  currentIndex === index
                    ? "bg-gray-800 scale-125"
                    : "bg-gray-400 hover:bg-gray-500"
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Email Section */}
      <div className="bg-[linear-gradient(135deg,_#e2ecf9,_#cfe0f5,_#e2ecf9)] flex flex-row flex-wrap justify-center items-center px-30 gap-20 py-30">
        <div className="flex flex-col max-w-[500px] gap-4">
          <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
            {t("landing_page.email_header")}
          </p>
          <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
            {t("landing_page.email_text")}
          </p>
        </div>
        <Card className="w-[600px] h-[730px] p-4 pb-0 overflow-hidden border">
          <iframe
            src="/mocked-email.html"
            title="Email Preview"
            className="w-full h-[700px] border-none rounded-md"
          />
        </Card>
      </div>

      {/* Footer Section */}
      <div className="bg-gray-100 px-60 mx-auto pt-10 pb-4">
        <div className="grid grid-cols-3 place-items-center mt-16 mb-6">
          <img src="/EUTOP_Logo.png" alt="EUTOP_Logo" width={"210px"} />
          <img src="/TUM_Logo.png" alt="TUM_Logo" width={"210px"} />
          <img src="/csee-logo.webp" alt="CSEE Logo" className="h-20 ml-2" />
        </div>
        <div>
          <Text className="text-center">{t("landing_page.credits")}</Text>
        </div>

        <div className="m-6 flex justify-center">
          <Button asChild variant="link">
            <span>
              <SquareArrowOutUpRight />
              <a href="https://www.eutop.com/de/" target="_blank">
                Visit EUTOP
              </a>
            </span>
          </Button>
        </div>
      </div>
    </div>
  );
}
