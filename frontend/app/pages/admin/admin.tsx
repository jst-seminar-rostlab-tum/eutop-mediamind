import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import Header from "~/custom-components/header";
import Layout from "~/custom-components/layout";
import Text from "~/custom-components/text";

export function Admin() {
  return (
    <>
      <Header />
      <Layout>
        <Text className="mt-6" hierachy={1}>
          Admin Settings
        </Text>

        <Tabs className="m-4">
          <TabsList defaultValue="organizations" className="w-full">
            <TabsTrigger value="organizations">Organizations</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
          </TabsList>

          <TabsContent value="organizations">
            <Card>
              <CardHeader>
                <CardTitle>Manage Organizations</CardTitle>
                <CardDescription>
                  Make changes to your Organizations here. You can add, edit or
                  delete them.
                </CardDescription>
              </CardHeader>
            </Card>
          </TabsContent>

          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>Manage Users</CardTitle>
                <CardDescription>
                  Make changes to your Users here. You can add, edit or delete
                  them.
                </CardDescription>
              </CardHeader>
            </Card>
          </TabsContent>

          <TabsContent value="subscriptions">
            <Card>
              <CardHeader>
                <CardTitle>Manage Subscriptions</CardTitle>
                <CardDescription>
                  Make changes to your Subscriptions here. You can add, edit or
                  delete them.
                </CardDescription>
              </CardHeader>
            </Card>
          </TabsContent>
        </Tabs>
      </Layout>
    </>
  );
}
