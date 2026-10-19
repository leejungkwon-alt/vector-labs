import React, { useState } from "react";
import { Modal, View, Text, TextInput, TouchableOpacity, FlatList, StyleSheet } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context"; // 👈 경고를 없애기 위해 import 경로 변경
import { colors, spacing, radius } from "@/theme";
import { CITY_LIST } from "@/constants/cities";

interface Props {
  visible: boolean;
  onClose: () => void;
  onSelect: (cityKey: string) => void;
  currentCityKey: string;
}

export function CityPickerModal({ visible, onClose, onSelect, currentCityKey }: Props) {
  const [search, setSearch] = useState("");

  const filtered = CITY_LIST.filter(c => 
    c.label.toLowerCase().includes(search.toLowerCase()) || 
    c.key.toLowerCase().includes(search.toLowerCase())
  );

  const CUSTOM_KEY = "__custom__";

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>출생지 선택</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
            <Text style={styles.closeText}>닫기</Text>
          </TouchableOpacity>
        </View>

        <TextInput
          style={styles.searchInput}
          placeholder="도시 이름 검색 (예: 서울, New York)"
          value={search}
          onChangeText={setSearch}
        />

        <FlatList
          data={filtered}
          keyExtractor={(item) => item.key}
          contentContainerStyle={{ paddingBottom: 40 }}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[styles.cityItem, currentCityKey === item.key && styles.selectedItem]}
              onPress={() => { onSelect(item.key); onClose(); }}
            >
              <Text style={[styles.cityText, currentCityKey === item.key && styles.selectedText]}>
                {item.label}
              </Text>
            </TouchableOpacity>
          )}
          ListFooterComponent={
            <TouchableOpacity 
              style={[styles.cityItem, { borderBottomWidth: 0, marginTop: 20, backgroundColor: colors.primary + "10" }]} 
              onPress={() => { onSelect(CUSTOM_KEY); onClose(); }}
            >
              <Text style={{ fontSize: 16, fontWeight: "700", color: colors.primary, textAlign: "center" }}>
                + 내 도시가 없나요? (직접 입력)
              </Text>
            </TouchableOpacity>
          }
          ListEmptyComponent={<Text style={{ textAlign: "center", marginTop: 20, color: colors.textMuted }}>검색 결과가 없습니다.</Text>}
        />
      </SafeAreaView>
    </Modal>
  );
}

export const CUSTOM_CITY_KEY = "__custom__";

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
