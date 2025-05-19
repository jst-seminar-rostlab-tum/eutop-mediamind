import { SquareArrowOutUpRight } from "lucide-react";
import { Button } from "~/components/ui/button";
import Header from "~/custom-components/header";
import Text from "~/custom-components/text";

export function Welcome() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <img
        src="Eutop_Wallpaper.svg"
        alt="Wallpaper"
        className="w-full object-cover"
      />

      <div className="p-8 flex flex-col flex-grow">
        <Text hierachy={1}>Welcome to MediaMind!</Text>
        <p className="p-4 block w-full text-lg leading-relaxed">
          Stay ahead in the fast-changing world of media with our Automated
          Press Analysis Tool. Keep your client teams informed and prepared with
          daily press reviews, personalized to your needs. Our platform extracts
          and compiles the most relevant news articles into concise, anonymized
          reports – delivered directly to your inbox each morning. Save time,
          stay informed, and focus on what matters most – delivering value to
          your clients.
        </p>

        <div className="flex justify-evenly p-14 pb-4">
          <img src="/EUTOP_Logo.svg" alt="EUTOP_Logo" />
          <img src="/TUM_Logo.svg" alt="TUM_Logo" />
        </div>

        <p className="flex justify-center">
          MediaMind was build in cooperation between EUTOP and the Technical
          University of Munich during the Javascript Technology Practicum
        </p>
      </div>

      <div className="p-4 w-full flex justify-center">
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
  );
}
