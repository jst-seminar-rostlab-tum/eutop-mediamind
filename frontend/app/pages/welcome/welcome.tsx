import { useEffect } from "react";
import { useNavigate } from "react-router";
import Text from "~/custom-components/text";
import { useAuthorization } from "~/hooks/use-authorization";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import { FeatureCarousel } from "./feature-carousel";
import { Button } from "~/components/ui/button";
import { SquareArrowOutUpRight } from "lucide-react";

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
      text: "Stay ahead in the fast-changing world of digital media",
      className: "text-4xl md:text-5xl font-medium leading-tight mb-2",
      delay: 0,
    },
    {
      text: "Media Mind",
      className: "text-5xl md:text-6xl font-bold leading-tight mb-2",
      delay: 0.3,
    },
    {
      text: "Your automated press analysis tool",
      className: "text-3xl md:text-4xl font-medium",
      delay: 0.6,
    },
  ];

  return (
    <>
      <div
        className="relative h-[500px] w-full bg-cover bg-center overflow-hidden"
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
      <div className="bg-muted">
        <div className="w-[80%] mx-auto">
          <FeatureCarousel />
        </div>
      </div>
      <div className="w-[60%] mx-auto">
        <div className="grid grid-cols-3 place-items-center mt-16 mb-6">
          <img src="/EUTOP_Logo.png" alt="EUTOP_Logo" width={"200px"} />
          <img src="/TUM_Logo.svg" alt="TUM_Logo" />
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
    </>
  );
}
{
  /*
    <>
      <img
        src="Eutop_Wallpaper.svg"
        alt="Wallpaper"
        className="w-full object-cover"
      />

      <Layout className="flex flex-col items-center">
        <Text className="mt-6" hierachy={1}>
          {t("landing_page.welcome")}
        </Text>
        <Text className="text-center">{t("landing_page.welcome_text")}</Text>
      </Layout>

      <div className="grid grid-cols-3 mx-auto max-w-7xl gap-6 my-16">
        <Card>
          <CardHeader>
            <CardTitle>Automated Content Ingestion</CardTitle>
          </CardHeader>
          <CardContent>
            <Text>
              Contiously scan hundreds of vetted sources - news sites, wire
              services, industry puplications, and especially newsletters - to
              capture every mention of your topics. Articles are anonymized and
              de-duplicated on the fly
            </Text>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Dynamic Keyword Optimization</CardTitle>
          </CardHeader>
          <CardContent>
            <Text>
              Our Machine Learning engine learns form past searches, your
              internal documents and live web trends to refine and expand your
              keyword sets - uncovering new angles, niche outlets and evolving
              terminology.
            </Text>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Powered Relevance Scoring</CardTitle>
          </CardHeader>
          <CardContent>
            <Text>
              Each article is rated against your objectives. MediaMind provides
              a transparent relevance score, a concise summary and an impact
              callout. Therefore you can prioritize high-value insighst at a
              glance.
            </Text>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Custom Daily Briefings</CardTitle>
          </CardHeader>
          <CardContent>
            <Text>
              Receive a consolidated PDF report every morning - complete with
              source citiations, direct links and sectional organization -
              tailored to each user's profile and workflow
            </Text>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Scalable & Low-Maintenance</CardTitle>
          </CardHeader>
          <CardContent>
            <Text>
              Built for efficiency with core monitoring tasks running
              automatically. This way your analysts can focus on interpretation
              and outreach rather than manual data collection.
            </Text>
          </CardContent>
        </Card>
      </div>

      <Layout className="grid grid-cols-3 place-items-center mt-16 mb-6">
        <img src="/EUTOP_Logo.png" alt="EUTOP_Logo" width={"200px"} />
        <img src="/TUM_Logo.svg" alt="TUM_Logo" />
        <img src="/csee-logo.webp" alt="CSEE Logo" className="h-20" />
      </Layout>
      <div>
        <Text className="text-center">{t("landing_page.credits")}</Text>
      </div>

      <Layout className="m-6 flex justify-center">
        <Button asChild variant="link">
          <span>
            <SquareArrowOutUpRight />
            <a href="https://www.eutop.com/de/" target="_blank">
              Visit EUTOP
            </a>
          </span>
        </Button>
      </Layout>
    </>
      );
    */
}
