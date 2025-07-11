import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import "./personal-settings-page.css";
import { useAuthorization } from "~/hooks/use-authorization";
import { client } from "types/api";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";

export default function PersonalSettings() {
  const { user, setMediamindUser } = useAuthorization();
  const { t } = useTranslation();
  const [editingField, setEditingField] = useState<
    "language" | "gender" | null
  >(null);
  const [language, setLanguage] = useState<"en" | "de">(user?.language ?? "en");
  const [gender, setGender] = useState<"male" | "female" | "divers">(
    user?.gender ?? "male",
  );

  const saveLanuage = async () => {
    if (!language || !user) {
      return;
    }
    try {
      await client.PUT("/api/v1/users/language", {
        params: { query: { language } },
      });
    } catch {
      toast.error(t("personal_settings.language_update_error"));
      return;
    }
    setMediamindUser?.({ ...user, language });
    setEditingField(null);
  };

  const saveGender = async () => {
    if (!gender || !user) {
      return;
    }
    try {
      await client.PUT("/api/v1/users/gender", {
        params: { query: { gender } },
      });
    } catch {
      toast.error(t("personal_settings.language_update_error"));
      return;
    }
    setMediamindUser?.({ ...user, gender });
    setEditingField(null);
  };

  return (
    <div className="w-full max-w-2xl space-y-6">
      <h1 className="text-lg font-semibold">{t("personal_settings.title")}</h1>

      <div>
        <div className="settings-entry">
          <div className="settings-entry-heading">
            {t("personal_settings.language")}
          </div>
          <div className="settings-entry-value-box">
            {editingField !== "language" ? (
              <span className="settings-entry-value">
                {language === "de" ? "Deutsch" : "English"}
              </span>
            ) : (
              <Select
                defaultValue={language ?? "en"}
                onValueChange={(value: "en" | "de") => {
                  setLanguage(value);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={"de"}>Deutsch</SelectItem>
                  <SelectItem value={"en"}>English</SelectItem>
                </SelectContent>
              </Select>
            )}
            {editingField !== "language" ? (
              <button
                className="update-button"
                onClick={() => setEditingField("language")}
              >
                {t("personal_settings.update_language")}
              </button>
            ) : (
              <button className="update-button" onClick={() => saveLanuage()}>
                {t("save_changes")}
              </button>
            )}
          </div>
        </div>
        <div className="settings-entry">
          <div className="settings-entry-heading">
            {t("personal_settings.gender")}
          </div>
          <div className="settings-entry-value-box">
            {editingField !== "gender" ? (
              <span className="settings-entry-value">
                {t(`personal_settings.${gender}`)}
              </span>
            ) : (
              <Select
                defaultValue={gender}
                onValueChange={(value: "male" | "female" | "divers") => {
                  setGender(value);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select Gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="divers">
                    {t("personal_settings.divers")}
                  </SelectItem>
                  <SelectItem value="female">
                    {t("personal_settings.female")}
                  </SelectItem>
                  <SelectItem value="male">
                    {t("personal_settings.male")}
                  </SelectItem>
                </SelectContent>
              </Select>
            )}
            {editingField !== "gender" ? (
              <button
                className="update-button"
                onClick={() => setEditingField("gender")}
              >
                {t("personal_settings.update_gender")}
              </button>
            ) : (
              <button className="update-button" onClick={() => saveGender()}>
                {t("save_changes")}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
