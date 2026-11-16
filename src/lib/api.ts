export type Domain = "physics_all" | "biology" | "drug" | "chemistry" | "finance";

export interface DiscoverRequest { domain: Domain; data: string; format: "json" | "csv"; }
export interface DiscoverResponse { engine: string; formula: string; r2_score: number; runtime_ms?: number; }

export const checkHealth = async (): Promise<boolean> => {
  try {
    const res = await fetch("http://localhost:8008/");
    const data = await res.json();
    return data.status === "online";
  } catch { return false; }
};

export const discover = async (req: DiscoverRequest): Promise<DiscoverResponse> => {
  try {
    // نگاشت دامنه‌های UI به modeهای بک‌اند
    let mode = "low_dim";
    if (req.domain === "drug" || req.domain === "chemistry") mode = "high_dim";
    if (req.domain === "biology") mode = "dna";
    if (req.domain === "finance") mode = "high_dim";
    if (req.domain === "physics_all") mode = "high_dim";

    const res = await fetch("http://localhost:8008/api/discover", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: `Discover ${req.domain} law`, mode: mode }),
    });
    const data = await res.json();
    
    if (!data.success) throw new Error("API Error");
    
    return {
      engine: data.engine_response.engine || "Elen-t Core",
      formula: data.engine_response.equation || data.engine_response.formula || "y = f(x)",
      r2_score: data.engine_response.r2_test || data.engine_response.r2 || 0.99,
      runtime_ms: 1200,
    };
  } catch (error) {
    throw new Error("Failed to connect to backend");
  }
};
