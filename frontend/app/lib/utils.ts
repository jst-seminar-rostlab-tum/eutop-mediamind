import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { useTranslation } from "react-i18next";
import i18n from "i18next";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function truncateAtWord(text: string, maxLength: number) {
  if (text.length <= maxLength) return text;
  const truncated = text.slice(0, maxLength);
  return truncated.slice(0, truncated.lastIndexOf(" ")) + "…";
}

export function formatDate(dateString: string) {
  const { i18n } = useTranslation();

  const locale = i18n.language == "de" ? "de-DE" : "en-US";

  try {
    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
      return "Invalid Date";
    }

    return date.toLocaleDateString(locale, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (error) {
    return dateString;
  }
}

export function getLocalizedContent(content: { [key: string]: string }) {
  if (content[i18n.language]) {
    return content[i18n.language];
  }

  if (content["en"]) {
    return content["en"];
  }
  if (content["de"]) {
    return content["de"];
  }
  return "Error";
}
