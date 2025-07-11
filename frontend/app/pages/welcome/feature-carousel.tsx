// FeatureCarousel.tsx
import { motion, useAnimation } from "framer-motion";
import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";

const features = [
  {
    title: "Automated Content Ingestion",
    text: "Contiously scan hundreds of vetted sources - news sites, wire services, industry puplications, and especially newsletters - to capture every mention of your topics. Articles are anonymized and de-duplicated on the fly",
  },
  {
    title: "Dynamic Keyword Optimization",
    text: "Our Machine Learning engine learns form past searches, your internal documents and live web trends to refine and expand your keyword sets - uncovering new angles, niche outlets and evolving terminology.",
  },
  {
    title: "AI Powered Relevance Scoring",
    text: "Each article is rated against your objectives. MediaMind provides a transparent relevance score, a concise summary and an impact callout. Therefore you can prioritize high-value insighst at a glance.",
  },
  {
    title: "Custom Daily Briefings",
    text: "Receive a consolidated PDF report every morning - complete with source citiations, direct links and sectional organization - tailored to each user's profile and workflow",
  },
  {
    title: "Scalable & Low-Maintenance",
    text: "Built for efficiency with core monitoring tasks running automatically. This way your analysts can focus on interpretation and outreach rather than manual data collection.",
  },
];

export function FeatureCarousel() {
  const controls = useAnimation();

  useEffect(() => {
    controls.start({
      x: ["0%", "-50%"],
      transition: {
        repeat: Infinity,
        repeatType: "loop",
        duration: 60,
        ease: "linear",
      },
    });
  }, [controls]);

  return (
    <div className="overflow-hidden w-full border-t border-b border-muted py-8 bg-muted">
      <motion.div animate={controls} className="flex gap-6 w-max">
        {/* Duplicate cards to create seamless looping */}
        {[...features, ...features].map((feature, index) => (
          <Card key={index} className="min-w-[300px] max-w-sm shrink-0">
            <CardHeader>
              <CardTitle>{feature.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xl text-muted-foreground leading-relaxed">
                {feature.text}
              </p>
            </CardContent>
          </Card>
        ))}
      </motion.div>
    </div>
  );
}
