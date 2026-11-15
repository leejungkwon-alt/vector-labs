import React, { useState, useEffect } from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
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
// 그래서 안드로이드에서는 "1974년  2월  24일" 을 직접 그린 한 줄 버튼으로 보여주고,
// 그 위에 투명한 네이티브 Picker 를 겹쳐서 눌렀을 때 선택 목록이 뜨게 한다.
const isAndroid = Platform.OS === 'android';

export default function BirthDateWheelPicker({ visible, onClose, onConfirm, initialDate }: Props) {
  const t = useT();
  // 안드로이드 하단 시스템 내비게이션 바에 시트가 가려지지 않도록 하단 여백을 잡는다.
  // (Modal 안에서는 인셋이 0으로 읽히는 기기가 있어, 3버튼 바 높이(약 48dp)를 덮는 최소값을 보장한다.)
  const insets = useSafeAreaInsets();
  const sheetBottomPadding =
    Platform.OS === 'web' ? 10 : Platform.OS === 'ios' ? 30 : Math.max(insets.bottom, 40) + 8;

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
  const itemLabel = (n: number, suffix: string) => `${n}${suffix}`;

  // 안드로이드 전용 한 줄 선택 칸: 보이는 글자는 직접 그리고, 투명 Picker 가 터치를 받아 목록을 연다.
  const renderAndroidField = (
    value: number,
    list: number[],
    onChange: (v: number) => void,
    suffix: string,
    flex: number,
  ) => (
    <View style={[styles.androidField, { flex }]}>
      <Text style={styles.androidFieldText} numberOfLines={1}>
        {itemLabel(value, suffix)}
        <Text style={styles.androidArrow}>{' ▾'}</Text>
      </Text>
      <Picker
        mode="dropdown"
        style={styles.androidPickerOverlay}
        selectedValue={value}
        onValueChange={(itemValue: number) => onChange(Number(itemValue))}
        dropdownIconColor="transparent"
      >
        {list.map((n) => (
          <Picker.Item key={n} label={itemLabel(n, suffix)} value={n} color={textColor} style={styles.androidItem} />
        ))}
      </Picker>
    </View>
  );

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

      {isAndroid ? (
        <View style={styles.androidRow}>
          {renderAndroidField(year, years, setYear, suffixes.year, 1.5)}
          {renderAndroidField(month, months, setMonth, suffixes.month, 1)}
          {renderAndroidField(day, days, setDay, suffixes.day, 1)}
        </View>
      ) : (
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
              <Picker.Item key={y} label={itemLabel(y, suffixes.year)} value={y} color={textColor} />
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
              <Picker.Item key={m} label={itemLabel(m, suffixes.month)} value={m} color={textColor} />
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
              <Picker.Item key={d} label={itemLabel(d, suffixes.day)} value={d} color={textColor} />
            ))}
          </Picker>
        </View>
      </View>
      )}
    </>
  );

  if (!visible) return null;

  // 웹(텔레그램 웹뷰 포함): React Native Modal 대신 fixed 오버레이 사용
  if (Platform.OS === 'web') {
    return (
      <View style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' } as any}>
        <View style={styles.overlay}>
          <View style={[styles.bottomSheet, { paddingBottom: sheetBottomPadding }]}>{pickerBody}</View>
        </View>
      </View>
    );
  }

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={[styles.bottomSheet, { paddingBottom: sheetBottomPadding }]}>{pickerBody}</View>
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
    height: isWeb ? 56 : 200,
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  // 연도/월/일 열: 연도는 "1990년" 처럼 길어서 넓게(1.6배) 잡고, 월/일은 남는 폭을 나눠 갖는다.
  column: { flex: 1, alignItems: 'center', justifyContent: 'center', width: '100%' },
  columnWide: { flex: 1.5 },
  // 안드로이드 전용 한 줄 선택 칸
  androidRow: { flexDirection: 'row', paddingHorizontal: 12, paddingVertical: 18 },
  androidField: {
    height: 52,
    marginHorizontal: 4,
    borderRadius: 12,
    backgroundColor: '#3A3A3A',
    alignItems: 'center',
    justifyContent: 'center',
  },
  androidFieldText: { color: '#FFFFFF', fontSize: 18, fontWeight: '600' },
  androidArrow: { color: '#9A9A9A', fontSize: 14, fontWeight: '400' },
  androidPickerOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0 },
  androidItem: { fontSize: 17 },
  picker: { width: '100%', color: textColor, height: isWeb ? 44 : undefined, marginHorizontal: 0 },
  pickerItem: { color: textColor, fontSize: 18 },
});