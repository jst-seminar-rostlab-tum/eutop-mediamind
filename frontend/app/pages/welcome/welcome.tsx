import { SquareArrowOutUpRight } from "lucide-react";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import Header from "~/custom-components/header";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";

export function Welcome() {
  return (
    <>
      <Layout>
        <Header />
      </Layout>

      <img
        src="Eutop_Wallpaper.svg"
        alt="Wallpaper"
        className="w-full object-cover"
      />

      <Layout className="place-items-center">
        <Text className="mt-6" hierachy={1}>
          Welcome to MediaMind!
        </Text>
        <Text className="text-center">
          Stay ahead in the fast-changing world of media with our Automated
          Press Analysis Tool. Keep your client teams informed and prepared with
          daily press reviews, personalized to your needs. Our platform extracts
          and compiles the most relevant news articles into concise, anonymized
          reports – delivered directly to your inbox each morning. Save time,
          stay informed, and focus on what matters most – delivering value to
          your clients.
        </Text>
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

      <Layout className="grid-cols-2 place-items-center mt-16">
        <img src="/EUTOP_Logo.png" alt="EUTOP_Logo" width={"200px"} />
        <img src="/TUM_Logo.svg" alt="TUM_Logo" />
      </Layout>
      <div>
        <Text className="text-center">
          MediaMind was build in cooperation between EUTOP and the Technical
          University of Munich during the Javascript Technology Practicum
        </Text>
      </div>

      <Layout className="m-6">
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
