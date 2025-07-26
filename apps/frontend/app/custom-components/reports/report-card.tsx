import type { ReportOverview } from "../../../types/model";
import { getDateComponents } from "~/lib/utils";
import { Button } from "~/components/ui/button";
import { Calendar, Download, Loader } from "lucide-react";
import { client } from "types/api";
import { RoleBadge } from "~/custom-components/dashboard/role-badge";
import { useTranslation } from "react-i18next";
import { useState } from "react";

interface ReportCardProps {
  report: ReportOverview;
}

export function ReportCard({ report }: ReportCardProps) {
  const [loading, setLoading] = useState(false);

  const dateComponents = getDateComponents(report.created_at);

  const loadReport = async () => {
    setLoading(true);
    const response = await client.GET("/api/v1/reports/{report_id}", {
      params: { path: { report_id: report.id } },
    });
    if (response.data) {
      window.open(response.data.s3_url!, "_blank");
    }
    setLoading(false);
  };

  const { t } = useTranslation();

  return (
    <div className="shadow-lg border-2 rounded-lg p-4 h-40 w-50 space-y-1 flex flex-col justify-between">
      <div className={"flex items-center gap-2"}>
        <Calendar className="w-6 h-6" />
        <div className={"flex items-baseline space-x-2"}>
          <span className={"font-semibold text-2xl"}>{dateComponents.day}</span>
          <div className={"flex space-x-1"}>
            <span>{dateComponents.month}</span>
            <span>{dateComponents.year}</span>
          </div>
        </div>
      </div>
      <div className={"flex gap-2 items-center"}>
        <div>
          {report.language === "en" ? (
            <RoleBadge variant={"en"} />
          ) : (
            <RoleBadge variant={"de"} />
          )}
        </div>
        <div>
          {report.time_slot === "morning" ? (
            <RoleBadge variant={"morning"} />
          ) : report.time_slot === "evening" ? (
            <RoleBadge variant={"evening"} />
          ) : (
            <RoleBadge variant={"afternoon"} />
          )}
        </div>
      </div>

      {report.s3_key ? (
        <Button onClick={loadReport} disabled={loading}>
          <>
            {t("reports.download")}
            {loading ? (
              <Loader className="h-4 w-4 animate-spin text-gray-500" />
            ) : (
              <Download />
            )}
          </>
        </Button>
      ) : (
        <Button disabled>
          {t("reports.download_unavailable")}
          <Download />
        </Button>
      )}
    </div>
  );
}
