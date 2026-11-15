import React, { useState, useEffect } from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useT } from '@/i18n';

interface Props {
  visible: boolean;
  onClose: () => void;
  onConfirm: (dateString: string) => void; 
  initialDate?: string; 
}

// 🌟 여기로 이동했습니다! (웹이면 검은색, 앱이면 흰색)
const isWeb = Platform.OS === 'web';
const textColor = isWeb ? '#000000' : '#FFFFFF';
// 안드로이드 네이티브 스피너는 칸이 좁으면 "10월" 같은 글자가 "10…" 로 잘린다.
// 그래서 안드로이드에서는 항목을 숫자만 보여주고, 년/월/일은 칸 위 라벨로 따로 표시한다.
const isAndroid = Platform.OS === 'android';

export default function BirthDateWheelPicker({ visible, onClose, onConfirm, initialDate }: Props) {
  const t = useT();

  const parseInitial = () => {
    const d = initialDate ? new Date(initialDate) : new Date(1990, 0, 1);
    return Number.isNaN(d.getTime()) ? new Date(1990, 0, 1) : d;
  };

  const initDate = parseInitial();
  const [year, setYear] = useState(initDate.getFullYear());
  const [month, setMonth] = useState(initDate.getMonth() + 1);
  const [day, setDay] = useState(initDate.getDate());

  const getDaysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate();
  const daysInMonth = getDaysInMonth(year, month);

  useEffect(() => {
    if (day > daysInMonth) setDay(daysInMonth);
  }, [month, year, day, daysInMonth]);

  const years = Array.from({ length: new Date().getFullYear() - 1920 + 1 }, (_, i) => new Date().getFullYear() - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  // 🌟 선택값이 목록 범위를 벗어나면(예: 범위 밖 연도, 2월 30일) 휠이 빈 칸으로 보이므로 항상 보정한다.
  useEffect(() => {
    if (!visible) return;
    if (!years.includes(year)) setYear(years[0]);
    if (month < 1 || month > 12) setMonth(1);
    if (day < 1 || day > daysInMonth) setDay(Math.min(Math.max(day, 1), daysInMonth));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  const suffixes = {
    year: t("datePicker.yearSuffix"),
    month: t("datePicker.monthSuffix"),
    day: t("datePicker.daySuffix"),
  };
  const itemLabel = (n: number, suffix: string) => (isAndroid ? String(n) : `${n}${suffix}`);
  const headerLabel = (suffix: string, fallback: string) => (suffix && suffix.trim() ? suffix.trim() : fallback);

  const handleConfirm = () => {
    const formattedMonth = String(month).padStart(2, '0');
    const formattedDay = String(day).padStart(2, '0');
    onConfirm(`${year}-${formattedMonth}-${formattedDay}`);
    onClose();
  };

  const pickerBody = (
    <>
      <View style={styles.header}>
        <TouchableOpacity onPress={onClose}>
          <Text style={styles.cancelText}>{t("datePicker.cancel")}</Text>
        </TouchableOpacity>
        <Text style={styles.title}>{t("datePicker.title")}</Text>
        <TouchableOpacity onPress={handleConfirm}>
          <Text style={styles.confirmText}>{t("datePicker.confirm")}</Text>
        </TouchableOpacity>
      </View>

      {isAndroid && (
        <View style={styles.colHeaderRow}>
          <Text style={[styles.colHeaderText, styles.columnWide]}>{headerLabel(suffixes.year, 'YYYY')}</Text>
          <Text style={styles.colHeaderText}>{headerLabel(suffixes.month, 'MM')}</Text>
          <Text style={styles.colHeaderText}>{headerLabel(suffixes.day, 'DD')}</Text>
        </View>
      )}

      <View style={styles.pickerContainer}>
        <View style={[styles.column, styles.columnWide]}>
          <Picker
            style={styles.picker}
            selectedValue={year}
            onValueChange={(itemValue: number) => setYear(Number(itemValue))}
            itemStyle={styles.pickerItem}
            dropdownIconColor={textColor}
          >
            {years.map((y) => (
              <Picker.Item key={y} label={itemLabel(y, suffixes.year)} value={y} color={textColor} style={isAndroid ? styles.androidItem : undefined} />
            ))}
          </Picker>
        </View>

        <View style={styles.column}>
          <Picker
            style={styles.picker}
            selectedValue={month}
            onValueChange={(itemValue: number) => setMonth(Number(itemValue))}
            itemStyle={styles.pickerItem}
            dropdownIconColor={textColor}
          >
            {months.map((m) => (
              <Picker.Item key={m} label={itemLabel(m, suffixes.month)} value={m} color={textColor} style={isAndroid ? styles.androidItem : undefined} />
            ))}
          </Picker>
        </View>

        <View style={styles.column}>
          <Picker
            style={styles.picker}
            selectedValue={day}
            onValueChange={(itemValue: number) => setDay(Number(itemValue))}
            itemStyle={styles.pickerItem}
            dropdownIconColor={textColor}
          >
            {days.map((d) => (
              <Picker.Item key={d} label={itemLabel(d, suffixes.day)} value={d} color={textColor} style={isAndroid ? styles.androidItem : undefined} />
            ))}
          </Picker>
        </View>
      </View>
    </>
  );

  if (!visible) return null;

  // 웹(텔레그램 웹뷰 포함): React Native Modal 대신 fixed 오버레이 사용
  if (Platform.OS === 'web') {
    return (
      <View style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' } as any}>
        <View style={styles.overlay}>
          <View style={styles.bottomSheet}>{pickerBody}</View>
        </View>
      </View>
    );
  }

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.bottomSheet}>{pickerBody}</View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'flex-end' },
  bottomSheet: {
    backgroundColor: isWeb ? '#FFFFFF' : '#2A2A2A', // 웹이면 흰색 배경, 앱이면 다크그레이
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: Platform.OS === 'ios' ? 30 : 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: isWeb ? '#E0E0E0' : '#444',
  },
  title: { color: isWeb ? '#000' : '#FFF', fontSize: 16, fontWeight: 'bold' },
  cancelText: { color: '#888', fontSize: 16 },
  confirmText: { color: '#4A90E2', fontSize: 16, fontWeight: 'bold' },
  pickerContainer: {
    flexDirection: 'row',
    height: isWeb ? 56 : isAndroid ? 64 : 200,
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  // 연도/월/일 열: 연도는 "1990년" 처럼 길어서 넓게(1.6배) 잡고, 월/일은 남는 폭을 나눠 갖는다.
  column: { flex: 1, alignItems: 'center', justifyContent: 'center', width: '100%' },
  columnWide: { flex: 1.5 },
  // 안드로이드 전용: 칸 위 년/월/일 라벨 (pickerContainer 와 같은 좌우 여백/비율)
  colHeaderRow: { flexDirection: 'row', paddingHorizontal: 8, paddingTop: 12 },
  colHeaderText: { flex: 1, textAlign: 'center', color: '#9A9A9A', fontSize: 13 },
  androidItem: { fontSize: 17 },
  picker: { width: '100%', color: textColor, height: isWeb ? 44 : undefined, marginHorizontal: 0 },
  pickerItem: { color: textColor, fontSize: 18 },
});