import { useEffect } from "react";
import { useNavigate } from "react-router";
import Text from "~/custom-components/text";
import { useAuthorization } from "~/hooks/use-authorization";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import { Button } from "~/components/ui/button";
import { SquareArrowOutUpRight } from "lucide-react";
import { Card } from "~/components/ui/card";
import { MockedDashboardPage } from "./mocked-dashboard";

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

  return (
    <>
      <div
        className="relative h-[50vh] w-full bg-cover bg-center overflow-hidden"
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
      <div className="pt-10 bg-[linear-gradient(to_bottom,_#3a4a5a_0%,_#dcdcdc_20%,_#f8f9fa_30%,_#f8f9fa_70%,_#dcdcdc_80%,_#556270_100%)]">
        {/* Features Section */}
        <div className="flex flex-col justify-center">
          <div className="w-[80%] p-20 mx-auto flex flex-wrap items-center gap-10 justify-center">
            <div className="w-170">
              <p className="text-4xl md:text-5xl font-semibold leading-tight mb-2">
                {t("landing_page.search_profile_header")}
              </p>
              <p className="text-2xl md:text-3xl font-medium leading-tight mb-2">
                {t("landing_page.search_profile_text")}
              </p>
            </div>
            <Card
              key="dashboard-prev"
              className="transform scale-100 max-w-[750px] h-195 border-8 p-0 px-2"
            >
              <MockedDashboardPage />
            </Card>
          </div>
        </div>

        {/* Footer Section */}
        <div className="w-[60%] mx-auto pt-10 pb-4">
          <div className="grid grid-cols-3 place-items-center mt-16 mb-6">
            <img src="/EUTOP_Logo.png" alt="EUTOP_Logo" width={"200px"} />
            <img src="/TUM_Logo.png" alt="TUM_Logo" />
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
    </>
  );
}
