import { SquareArrowOutUpRight } from "lucide-react";
import { useEffect } from "react";
import { useNavigate } from "react-router";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import { useAuthorization } from "~/hooks/use-authorization";
import { useTranslation } from "react-i18next";

export function Welcome() {
  const { isSignedIn, user } = useAuthorization();
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    if (isSignedIn && user?.organization_id) {
      navigate("/dashboard");
    }
  }, [isSignedIn, user?.organization_id, navigate]);
  return (
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
}
