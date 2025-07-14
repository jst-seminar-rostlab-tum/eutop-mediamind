import { useTranslation } from "react-i18next";
import { Link } from "react-router";
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbPage,
} from "~/components/ui/breadcrumb";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";
import { useAuthorization } from "~/hooks/use-authorization";
import { OrganisationSettingsPage } from "~/pages/organisation-settings/organisation-settings-page";

export default function OrganisationSettings() {
  const { t } = useTranslation();
  const { user } = useAuthorization();

  return (
    <Layout noOverflow={true}>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link to="/dashboard">{t("breadcrumb_home")}</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>{t("organisation_settings.title")}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <Text hierachy={2}>{t("organisation_settings.title")}</Text>
      {user?.organization_id && (
        <OrganisationSettingsPage organisationId={user?.organization_id} />
      )}
    </Layout>
  );
}
