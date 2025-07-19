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
import { MockedBreakingNews } from "./mocked-breaking-news";
import { exampleArticle, exampleProfile } from "./mock-data";
import i18n from "~/i18n";

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
      text: "Media Mind",
      className: "text-5xl md:text-6xl font-bold leading-tight mb-2",
      delay: 0.1,
    },
    {
      text: t("landing_page.header_slogan"),
      className: "text-4xl md:text-5xl font-medium",
      delay: 0.4,
    },
  ];

  const [profile, setProfile] = useState(exampleProfile);

  const features = [
    {
      header: t("landing_page.topics_header"),
      text: t("landing_page.topics_text"),
      card: <MockedTopics profile={profile} setProfile={setProfile} />,
      key: "topics",
      zoom: 1.15,
      height: "h-120",
      width: "w-170",
    },
    {
      header: t("landing_page.dashboard_header"),
      text: t("landing_page.dashboard_text"),
      card: <MockedDashboardPage />,
      key: "dashboard",
      zoom: 0.9,
      height: "h-190",
      width: "w-170",
    },
    {
      header: t("landing_page.search_profile_header"),
      text: t("landing_page.search_profile_text"),
      card: <MockedSearchProfileOverview />,
      key: "search-profile",
      zoom: 0.75,
      height: "h-230",
      width: "w-260",
    },
    {
      header: t("landing_page.breaking_header"),
      text: t("landing_page.breaking_text"),
      card: <MockedBreakingNews />,
      key: "breaking-news",
      zoom: 0.85,
      height: "h-190",
      width: "w-220",
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
      height: "h-230",
      width: "w-260",
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
      setHasUserInteracted(false); // If user has interacted: Resume autoplay after 15 sec
    }, 15000);

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
          <div className="flex items-center relative z-10 w-full min-h-[1000px] pt-15 pb-25">
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
                className="w-[80%] h-full gap-14 gap-y-0 flex flex-wrap justify-center items-center mx-auto"
              >
                <div className="flex flex-col max-w-[500px] h-[310px] justify-center items-center gap-4">
                  <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
                    {features[currentIndex].header}
                  </p>
                  <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
                    {features[currentIndex].text}
                  </p>
                </div>
                <div className="w-190 h-190 flex justify-center items-center">
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
              className="cursor-pointer"
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
              className="cursor-pointer"
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
          <div className="absolute bottom-20 left-0 right-0 flex justify-center gap-5 z-20">
            {features.map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentIndex(index);
                  setHasUserInteracted(true);
                }}
                className={`h-3 w-3 rounded-full transition-all duration-300 cursor-pointer ${
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
        <Card className="w-[600px] h-[735px] p-4 pb-0 overflow-hidden border">
          {i18n.language == "en" ? (
            <iframe
              src="/mocked-email-en.html"
              title="Email Preview"
              className="w-full h-[710px] border-none rounded-md"
            />
          ) : (
            <iframe
              src="/mocked-email-de.html"
              title="Email Preview"
              className="w-full h-[710px] border-none rounded-md"
            />
          )}
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
