export interface PdbMetadata {
  pdbId: string;
  name: string;
  classification: string;
  atomCount: number;
  residueCount: number;
  chains: string[];
  helixCount: number;
  sheetCount: number;
}

export interface PresetMolecule {
  pdbId: string;
  label: string;
  subtitle: string;
  tag: string;
}

export const PRESET_MOLECULES: PresetMolecule[] = [
  { pdbId: "1CRN", label: "Crambin", subtitle: "Plant Seed Protein · 46 res", tag: "DEFAULT" },
  { pdbId: "1UBQ", label: "Ubiquitin", subtitle: "Regulatory Protein · 76 res", tag: "FOLDING" },
  { pdbId: "1BNA", label: "B-DNA Helix", subtitle: "Dodecamer Duplex · 24 nt", tag: "NUCLEIC" },
  { pdbId: "4HHB", label: "Hemoglobin", subtitle: "Deoxy Tetramer · 4 chains", tag: "HEME" },
  { pdbId: "6LU7", label: "Mpro Protease", subtitle: "Covalent Inhibitor · Complex", tag: "DRUG-TARGET" },
];

export function parsePdbMetadata(pdbContent: string, pdbId: string): PdbMetadata {
  const lines = pdbContent.split(/\r?\n/);
  let classification = "MACROMOLECULAR COMPLEX";
  const titleParts: string[] = [];
  let compndName = "";
  let atomCount = 0;
  let helixCount = 0;
  let sheetCount = 0;
  const residueKeys = new Set<string>();
  const chainsSet = new Set<string>();

  for (const line of lines) {
    if (line.startsWith("HEADER")) {
      const cls = line.slice(10, 50).trim();
      if (cls) classification = cls;
    } else if (line.startsWith("TITLE")) {
      const part = line.slice(10, 80).trim();
      if (part) titleParts.push(part);
    } else if (line.startsWith("COMPND") && line.includes("MOLECULE:")) {
      const match = line.match(/MOLECULE:\s*([^;]+)/i);
      if (match?.[1]) compndName = match[1].trim();
    } else if (line.startsWith("HELIX")) {
      helixCount += 1;
    } else if (line.startsWith("SHEET")) {
      sheetCount += 1;
    } else if (line.startsWith("ATOM") || line.startsWith("HETATM")) {
      atomCount += 1;
      const chain = (line.slice(21, 22) || "A").trim() || "A";
      const resSeq = line.slice(22, 26).trim();
      chainsSet.add(chain);
      if (resSeq) residueKeys.add(`${chain}:${resSeq}`);
    }
  }

  const rawTitle = compndName || titleParts.join(" ").replace(/\s+/g, " ").trim();
  const formattedTitle = rawTitle
    ? rawTitle.toLowerCase().replace(/(^\w|\s\w)/g, (m) => m.toUpperCase()).slice(0, 72)
    : `Structure ${pdbId.toUpperCase()}`;

  return {
    pdbId: pdbId.toUpperCase(),
    name: formattedTitle,
    classification,
    atomCount,
    residueCount: residueKeys.size,
    chains: Array.from(chainsSet),
    helixCount,
    sheetCount,
  };
}

export function sanitizePdbId(input: string): string {
  return input.trim().toUpperCase().replace(/[^A-Z0-9_]/g, "").slice(0, 20);
}

export const FALLBACK_1CRN_PDB = `HEADER    PLANT PROTEIN                           30-APR-81   1CRN
TITLE     WATER STRUCTURE OF A HYDROPHOBIC PROTEIN AT ATOMIC RESOLUTION
COMPND    MOL_ID: 1; MOLECULE: CRAMBIN; CHAIN: A
ATOM      1  N   THR A   1      17.047  14.099   3.625  1.00 13.79           N
ATOM      2  CA  THR A   1      16.967  12.784   4.338  1.00 10.80           C
ATOM      3  C   THR A   1      15.685  12.755   5.133  1.00  9.19           C
ATOM      4  O   THR A   1      15.268  13.825   5.594  1.00  9.85           O
END
`;
