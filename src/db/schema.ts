import { pgTable, serial, varchar, text, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";

export const molecularStructures = pgTable("molecular_structures", {
  id: serial("id").primaryKey(),
  pdbId: varchar("pdb_id", { length: 16 }).notNull().unique(),
  name: text("name").notNull(),
  classification: text("classification").notNull().default("PROTEIN STRUCTURE"),
  atomCount: integer("atom_count").notNull().default(0),
  residueCount: integer("residue_count").notNull().default(0),
  pdbContent: text("pdb_content").notNull(),
  isFavorite: boolean("is_favorite").notNull().default(false),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const simulationRuns = pgTable("simulation_runs", {
  id: serial("id").primaryKey(),
  pdbId: varchar("pdb_id", { length: 16 }).notNull(),
  representation: varchar("representation", { length: 32 }).notNull(),
  temperature: integer("temperature").notNull(),
  durationNs: integer("duration_ns").notNull().default(50),
  status: varchar("status", { length: 32 }).notNull().default("completed"),
  energyKcalMol: text("energy_kcal_mol").notNull(),
  rmsdAngstrom: text("rmsd_angstrom").notNull(),
  logs: jsonb("logs").$type<string[]>().notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const workspaceDeployments = pgTable("workspace_deployments", {
  id: serial("id").primaryKey(),
  serviceName: text("service_name").notNull(),
  branch: text("branch").notNull(),
  environment: text("environment").notNull(),
  status: varchar("status", { length: 32 }).notNull().default("live"),
  commitHash: varchar("commit_hash", { length: 16 }).notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const terminalHistory = pgTable("terminal_history", {
  id: serial("id").primaryKey(),
  command: text("command").notNull(),
  output: text("output").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const aiMessages = pgTable("ai_messages", {
  id: serial("id").primaryKey(),
  role: varchar("role", { length: 16 }).notNull(),
  content: text("content").notNull(),
  contextPdb: varchar("context_pdb", { length: 16 }),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export type MolecularStructure = typeof molecularStructures.$inferSelect;
export type SimulationRun = typeof simulationRuns.$inferSelect;
export type WorkspaceDeployment = typeof workspaceDeployments.$inferSelect;
export type TerminalEntry = typeof terminalHistory.$inferSelect;
export type AiMessage = typeof aiMessages.$inferSelect;
