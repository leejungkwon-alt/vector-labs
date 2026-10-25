import React, { useState } from "react";
import { Modal, View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, spacing, radius } from "@/theme";
import { TIMEZONE_LIST } from "@/constants/timezones";
import { useT } from "@/i18n";

interface Props {
  visible: boolean;
  onClose: () => void;
  onSelect: (tzKey: string) => void;
  currentTz: string;
}

export function TimezonePickerModal({ visible, onClose, onSelect, currentTz }: Props) {
  const [search, setSearch] = useState("");
  const t = useT();

  const filtered = TIMEZONE_LIST.filter(c => 
    c.label.toLowerCase().includes(search.toLowerCase()) || 
    c.key.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{t("timezoneModal.title")}</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
            <Text style={styles.closeText}>{t("common.close")}</Text>
          </TouchableOpacity>
        </View>

        <TextInput
          style={styles.searchInput}
          placeholder={t("timezoneModal.placeholder")}
          value={search}
          onChangeText={setSearch}
        />

        <FlatList
          data={filtered}
          keyExtractor={(item) => item.key}
          contentContainerStyle={{ paddingBottom: 40 }}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[styles.cityItem, currentTz === item.key && styles.selectedItem]}
              onPress={() => { onSelect(item.key); onClose(); }}
            >
              <Text style={[styles.cityText, currentTz === item.key && styles.selectedText]}>
                {item.label}
              </Text>
            </TouchableOpacity>
          )}
          ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20, color: colors.textMuted }}>{t("timezoneModal.noResults")}</Text>}
        />
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg, padding: spacing.lg },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 16 },
  title: { fontSize: 20, fontWeight: "700", color: colors.text },
  closeBtn: { padding: 8 },
  closeText: { fontSize: 16, color: colors.primary, fontWeight: "600" },
  searchInput: { backgroundColor: colors.surface, padding: 12, borderRadius: radius.md, borderWidth: 1, borderColor: colors.border, marginBottom: 16, fontSize: 15 },
  cityItem: { paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: colors.border },
  selectedItem: { backgroundColor: colors.primary + "10" },
  cityText: { fontSize: 16, color: colors.text },
  selectedText: { color: colors.primary, fontWeight: "700" },
});
