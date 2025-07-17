import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import Text from "~/custom-components/text";
import { useAuthorization } from "~/hooks/use-authorization";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import { Button } from "~/components/ui/button";
import { SquareArrowOutUpRight } from "lucide-react";
import { Card } from "~/components/ui/card";
import { MockedDashboardPage } from "./mocked-dashboard";
import { MockedTopics } from "./mocked-topics";
import { MockedSearchProfileOverview } from "./mocked-search-profile";

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

  // for mocked topics
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

  const [profile, setProfile] = useState(exampleProfile);

  return (
    <div>
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
      <div className="pt-10 bg-[linear-gradient(to_bottom,_#556270_0%,_#dcdcdc_10%,_#f8f9fa_15%,_#f8f9fa_70%,_#dcdcdc_80%,_#556270_100%)]">
        <div className="w-[80%] mx-auto flex flex-col justify-center gap-30 pt-40 ">
          <div className="flex flex-row flex-wrap justify-center items-center gap-20">
            <div className="flex flex-col max-w-[500px] gap-4">
              <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
                {t("landing_page.topics_header")}
              </p>
              <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
                {t("landing_page.topics_text")}
              </p>
            </div>
            <Card
              key="keywords-prev"
              style={{ zoom: 1.15 }}
              className="transform scale-110 max-w-300 h-110 border-8 p-6 pt-4"
            >
              <MockedTopics profile={profile} setProfile={setProfile} />
            </Card>
          </div>

          <div className="flex flex-row flex-wrap justify-center items-center gap-20">
            <div className="flex flex-col max-w-[500px] gap-4">
              <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
                {t("landing_page.dashboard_header")}
              </p>
              <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
                {t("landing_page.dashboard_text")}
              </p>
            </div>

            <Card
              key="dashboard-prev"
              style={{ zoom: 0.95 }}
              className="max-w-300 h-195 border-8 p-0"
            >
              <MockedDashboardPage />
            </Card>
          </div>
          <div className="flex flex-row flex-wrap justify-center items-center gap-20">
            <div className="flex flex-col max-w-[500px] gap-4">
              <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
                {t("landing_page.search_profile_header")}
              </p>
              <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
                {t("landing_page.search_profile_text")}
              </p>
            </div>

            <Card
              key="sp-prev"
              style={{ zoom: 0.7 }}
              className="h-245 max-w-300 border-8 p-6 py-3 overflow-hidden"
            >
              <MockedSearchProfileOverview />
            </Card>
          </div>
        </div>

        {/* Footer Section */}
        <div className="w-[60%] mx-auto pt-10 pb-4">
          <div className="grid grid-cols-3 place-items-center mt-16 mb-6">
            <img src="/EUTOP_Logo.png" alt="EUTOP_Logo" width={"210px"} />
            <img src="/TUM_Logo.png" alt="TUM_Logo" width={"210px"} />
            <img src="/csee-logo.webp" alt="CSEE Logo" className="h-20" />
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
    </div>
  );
}
