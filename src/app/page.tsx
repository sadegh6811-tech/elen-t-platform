import { db } from "@/db";
import {
  aiMessages,
  simulationRuns,
  terminalHistory,
  workspaceDeployments,
} from "@/db/schema";
import { ensureWorkspaceSeeded } from "@/db/seed";
import ElenkWorkspace from "@/components/workspace/ElenkWorkspace";
import { desc } from "drizzle-orm";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  let runs: (typeof simulationRuns.$inferSelect)[] = [];
  let deployments: (typeof workspaceDeployments.$inferSelect)[] = [];
  let terminal: (typeof terminalHistory.$inferSelect)[] = [];
  let messages: (typeof aiMessages.$inferSelect)[] = [];

  try {
    await ensureWorkspaceSeeded();
    [runs, deployments, terminal, messages] = await Promise.all([
      db.select().from(simulationRuns).orderBy(desc(simulationRuns.createdAt)).limit(8),
      db.select().from(workspaceDeployments).orderBy(workspaceDeployments.id),
      db.select().from(terminalHistory).orderBy(terminalHistory.id).limit(40),
      db.select().from(aiMessages).orderBy(aiMessages.id).limit(40),
    ]);
  } catch (err) {
    console.error("Workspace hydration warning:", err);
  }

  return (
    <ElenkWorkspace
      initialRuns={runs}
      initialDeployments={deployments}
      initialTerminal={terminal}
      initialAiMessages={messages}
    />
  );
}
