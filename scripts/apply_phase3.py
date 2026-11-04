import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def write_poem_store():
    content = '''import { create } from "zustand";
import type { PoemCard } from "../../types";

interface PoemState {
  currentPoem: PoemCard | null;
  collection: PoemCard[];
  setCurrentPoem: (poem: PoemCard, collection?: PoemCard[]) => void;
}

export const usePoemStore = create<PoemState>((set) => ({
  currentPoem: null,
  collection: [],
  setCurrentPoem: (poem, collection = []) => set({ currentPoem: poem, collection }),
}));
'''
    p = ROOT / "frontend" / "src" / "store" / "poemStore.ts"
    p.write_text(content, encoding="utf-8")
    print("[OK] poemStore.ts created")

def write_collection():
    content = '''import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Image } from "react-native";
import { colors, spacing } from "@/theme";
import { router } from "expo-router";
import { usePoemStore } from "@/store/poemStore";
import { useAuthStore } from "@/store/authStore";

export default function CollectionScreen() {
  const user = useAuthStore((s) => s.user);
  const { collection } = usePoemStore();
  const isPremium = user?.tier === "premium" || user?.tier === "subscription";

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Poem Collection</Text>
        <Text style={styles.subtitle}>{collection[0]?.element || ""} x {collection.length}</Text>
      </View>
      <ScrollView contentContainerStyle={styles.grid}>
        {collection.map((poem, i) => {
          const locked = poem.tier === "premium" && !isPremium;
          return (
            <View key={i} style={[styles.card, locked && { opacity: 0.7 }]}>
              <Image source={{ uri: "/assets/poems/" + poem.id + "_calligraphy.svg" }} style={styles.cardImg} />
              <Text style={styles.cardTitle}>{poem.title}</Text>
              <Text style={styles.cardRelation}>{poem.relation_kr}</Text>
              {locked && (<View style={styles.lockOverlay}><Text style={styles.lockText}>LOCK</Text></View>)}
            </View>
          );
        })}
      </ScrollView>
      {!isPremium && (
        <View style={styles.footer}>
          <Text style={styles.footerText}>Upgrade to see all 25 poems</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  header: { padding: spacing.lg, paddingTop: spacing.xl, backgroundColor: colors.surface, borderBottomWidth: 1, borderBottomColor: colors.border },
  backBtn: { marginBottom: spacing.md },
  backText: { color: colors.primary, fontSize: 16, fontWeight: "600" },
  title: { fontSize: 28, fontWeight: "800", color: colors.text, marginBottom: 4 },
  subtitle: { fontSize: 16, color: colors.textMuted },
  grid: { padding: spacing.md, flexDirection: "row", flexWrap: "wrap", gap: spacing.md, justifyContent: "center" },
  card: { width: "45%", backgroundColor: colors.surface, borderRadius: 16, padding: spacing.md, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" },
  cardImg: { width: "100%", height: 80, borderRadius: 8, marginBottom: 8, backgroundColor: colors.bgMuted },
  cardTitle: { fontSize: 16, fontWeight: "700", color: colors.text, textAlign: "center", marginBottom: 4 },
  cardRelation: { fontSize: 12, color: colors.textMuted },
  lockOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: "rgba(0,0,0,0.4)", alignItems: "center", justifyContent: "center" },
  lockText: { color: "#fff", fontWeight: "700", fontSize: 14 },
  footer: { padding: spacing.lg, backgroundColor: colors.primarySoft, alignItems: "center" },
  footerText: { color: colors.primary, fontWeight: "600" }
});
'''
    p = ROOT / "frontend" / "app" / "collection.tsx"
    p.write_text(content, encoding="utf-8")
    print("[OK] collection.tsx replaced")

def patch_home():
    p = ROOT / "frontend" / "app" / "(tabs)" / "home.tsx"
    t = p.read_text(encoding="utf-8")
    if "usePoemStore" in t:
        print("[SKIP] home.tsx already patched")
        return
    t = t.replace(
        'import { useProfileStore } from "@/store/profileStore";',
        'import { useProfileStore } from "@/store/profileStore";\nimport { usePoemStore } from "@/store/poemStore";'
    )
    t = t.replace(
        "const [expanded, setExpanded] = useState<Record<string, boolean>>({ core: true });",
        "const [expanded, setExpanded] = useState<Record<string, boolean>>({ core: true });\n  const setCurrentPoem = usePoemStore((s) => s.setCurrentPoem);"
    )
    hook = "\n\n  useEffect(() => {\n    if (data?.report?.sections?.lucky_code?.poem) {\n      const poem = data.report.sections.lucky_code.poem;\n      const collection = (poem as any).collection || [];\n      setCurrentPoem(poem, collection);\n    }\n  }, [data, setCurrentPoem]);\n"
    t = t.replace("  const toggleSection = (id: string) =>", hook + "\n  const toggleSection = (id: string) =>")
    p.write_text(t, encoding="utf-8")
    print("[OK] home.tsx patched")

def patch_content_writer():
    p = ROOT / "app" / "services" / "content_writer.py"
    t = p.read_text(encoding="utf-8")
    if '"collection": collection' in t:
        print("[SKIP] content_writer.py already patched")
        return
    old = '    return {\n        "id": match["id"],\n        "element": match["element"],'
    new = (
        '    collection = []\n'
        '    for _p in poems:\n'
        '        if _p.get("element_idx") == yong_idx:\n'
        '            tr_p = _p.get("translations", {}).get(lang) or _p.get("translations", {}).get("ko") or {}\n'
        '            title_map_p = _p.get("title", {})\n'
        '            collection.append({\n'
        '                "id": _p["id"],\n'
        '                "element": _p["element"],\n'
        '                "element_idx": yong_idx,\n'
        '                "relation": _p.get("relation"),\n'
        '                "relation_kr": POEM_RELATION_KR.get(_p.get("relation"), ""),\n'
        '                "title": title_map_p.get(lang) or title_map_p.get("ko") or _p["id"],\n'
        '                "sijo_ko": _p.get("sijo_ko", ""),\n'
        '                "romanization": _p.get("romanization", ""),\n'
        '                "commentary": tr_p.get("commentary", ""),\n'
        '                "interpretation": tr_p.get("interpretation", ""),\n'
        '                "practice": tr_p.get("practice", ""),\n'
        '                "keywords": _p.get("keywords", []),\n'
        '                "tier": _p.get("tier", "premium"),\n'
        '                "calligraphy_image": _p.get("calligraphy_image", ""),\n'
        '                "wallpaper_image": _p.get("wallpaper_image", ""),\n'
        '            })\n\n'
        '    return {\n        "id": match["id"],\n        "element": match["element"],'
    )
    if old not in t:
        print("[ERR] content_writer.py anchor not found")
        return
    t = t.replace(old, new, 1)
    old2 = '        "tier": match.get("tier", "premium"),\n    }'
    new2 = '        "tier": match.get("tier", "premium"),\n        "collection": collection,\n    }'
    t = t.replace(old2, new2, 1)
    p.write_text(t, encoding="utf-8")
    print("[OK] content_writer.py patched")

if __name__ == "__main__":
    write_poem_store()
    write_collection()
    patch_home()
    patch_content_writer()
